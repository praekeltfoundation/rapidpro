# Generated by Django 1.11.6 on 2017-12-14 17:15

import json
import os
import time
from datetime import timedelta
from uuid import UUID

from django_redis import get_redis_connection

from django.db import migrations, transaction
from django.db.models import Prefetch
from django.utils import timezone

from temba.utils import chunk_list

CACHE_KEY_HIGHPOINT = "msgs_mig_highpoint"
CACHE_KEY_MAX_RUN_ID = "msgs_mig_max_run_id"


def backfill_flowrun_messages(FlowRun, FlowStep, Msg):
    cache = get_redis_connection()

    # are we running on just a partition of the runs?
    partition = os.environ.get("PARTITION")
    if partition is not None:
        partition = int(partition)
        if partition < 0 or partition > 3:
            raise ValueError("Partition must be 0-3")

        print("Migrating runs in partition %d" % partition)

    # has this migration been run before but didn't complete?
    highpoint = None
    if partition is not None:
        highpoint = cache.get(CACHE_KEY_HIGHPOINT + (":%d" % partition))
    if highpoint is None:
        highpoint = cache.get(CACHE_KEY_HIGHPOINT)

    highpoint = 0 if highpoint is None else int(highpoint)

    max_run_id = cache.get(CACHE_KEY_MAX_RUN_ID)
    if max_run_id is None:
        max_run = FlowRun.objects.filter(flow__is_active=True).order_by("-id").first()
        if max_run:
            max_run_id = max_run.id
            cache.set(CACHE_KEY_MAX_RUN_ID, max_run_id, 60 * 60 * 24 * 7)
        else:
            return  # no work to do here
    else:
        max_run_id = int(max_run_id)

    # get all flow runs we're going to migrate
    runs = FlowRun.objects.filter(flow__is_active=True).only("id").order_by("id")

    if highpoint:
        print("Resuming from previous highpoint at run #%d" % highpoint)
        runs = runs.filter(id__gt=highpoint)

    if max_run_id:
        print("Migrating runs up to run #%d" % max_run_id)
        runs = runs.filter(id__lte=max_run_id)

    remaining_estimate = max_run_id - highpoint
    print("Estimated %d runs need to be migrated" % remaining_estimate)

    num_updated = 0
    num_trimmed = 0
    start = None

    # we want to prefetch step messages with each flow run
    steps_prefetch = Prefetch("steps", queryset=FlowStep.objects.only("id", "run"))
    steps_messages_prefetch = Prefetch("steps__messages", queryset=Msg.objects.only("id"))

    for run_batch in chunk_list(runs.using("direct").iterator(), 1000):
        # first call is gonna take a while to complete the query on the db, so start timer after that
        if start is None:
            start = time.time()

        with transaction.atomic():
            if partition is not None:
                run_ids = [r.id for r in run_batch if ((r.id + partition) % 4 == 0)]
            else:
                run_ids = [r.id for r in run_batch]

            batch = (
                FlowRun.objects.filter(id__in=run_ids)
                .order_by("id")
                .prefetch_related(steps_prefetch, steps_messages_prefetch)
            )

            for run in batch:
                msg_ids = set()
                for step in run.steps.all():
                    for msg in step.messages.all():
                        msg_ids.add(msg.id)

                path = json.loads(run.path) if run.path else []
                current_node_uuid = path[-1]["node_uuid"] if path else None

                run.current_node_uuid = UUID(current_node_uuid) if current_node_uuid else None
                run.message_ids = sorted(msg_ids) if msg_ids else None

                if run.current_node_uuid or run.message_ids:
                    run.save(update_fields=("current_node_uuid", "message_ids"))

                highpoint = run.id
                if partition is not None:
                    cache.set(CACHE_KEY_HIGHPOINT + (":%d" % partition), str(run.id), 60 * 60 * 24 * 7)
                else:
                    cache.set(CACHE_KEY_HIGHPOINT, str(run.id), 60 * 60 * 24 * 7)

        num_updated += len(batch)
        updated_per_sec = num_updated / (time.time() - start)

        # figure out estimated time remaining
        num_remaining = ((max_run_id - highpoint) // 4) if partition is not None else (max_run_id - highpoint)
        time_remaining = num_remaining / updated_per_sec
        finishes = timezone.now() + timedelta(seconds=time_remaining)
        status = " > Updated %d runs of ~%d (%2.2f per sec) Est finish: %s" % (
            num_updated,
            remaining_estimate,
            updated_per_sec,
            finishes,
        )

        if partition is not None:
            status += " [PARTITION %d]" % partition

        print(status)

    if start:
        print(
            "Run messages migration completed in %d mins. %d paths were trimmed"
            % ((int(time.time() - start) // 60), num_trimmed)
        )


def apply_manual():
    from temba.flows.models import FlowRun, FlowStep
    from temba.msgs.models import Msg

    backfill_flowrun_messages(FlowRun, FlowStep, Msg)


def apply_as_migration(apps, schema_editor):
    FlowRun = apps.get_model("flows", "FlowRun")
    FlowStep = apps.get_model("flows", "FlowStep")
    Msg = apps.get_model("msgs", "Msg")
    backfill_flowrun_messages(FlowRun, FlowStep, Msg)


class Migration(migrations.Migration):

    dependencies = [("flows", "0136_flowrun_message_and_current_node")]

    operations = [migrations.RunPython(apply_as_migration)]
