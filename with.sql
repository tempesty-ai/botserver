with
  app_pod_data as (
    select
      target_id,
      pod_name
    from
      (
        select
          target_id,
          system_attributes['container_key'] as pod_id
        from
          target_merge_dist app final
        where
          target_kind = 'application'
          and toDateTime ('2026-03-31 15:00:00') >= created_time
          and (
            deleted_time = 0
            or deleted_time >= toDateTime ('2026-03-30 15:00:00')
          )
      ) app
      inner join (
        select
          target_id as pod_id,
          argMax (system_attributes['name'], updated_time) as pod_name
        from
          target_merge_dist final
        where
          target_kind = 'pod'
          and toDateTime ('2026-03-31 15:00:00') >= created_time
          and (
            deleted_time = 0
            or deleted_time >= toDateTime ('2026-03-30 15:00:00')
          )
        group by
          pod_id
      ) pod on app.pod_id = pod.pod_id
  )
SELECT
  collect_time,
  start_time,
  was_id,
  tid,
  txn_name,
  client_ip,
  login_name,
  pool_name as pool,
  thread_cpu_time as txn_cpu_time,
  elapsed_time,
  if (
    class_name = = '',
    method_name,
    concat(class_name, '.', method_name)
  ) as class_method,
  method_type,
  pod_name,
  elapsed_time - (sql_elapsed_time + remote_elapsed_time) as app_elapsed_time,
  sql_elapsed_time,
  fetch_count as sql_fetch_count,
  remote_elapsed_time,
  sql_exec_count as sql_executions,
  remote_count as remote_executions,
  tx_code,
  guid,
  filler1,
  filler2,
  filler3,
  filler4
FROM
  application_active_txn_v2_dist atxn
  left join (
    select
      *
    from
      app_pod_data
  ) pod on atxn.was_id = pod.target_id
WHERE
  was_id IN (
    SELECT DISTINCT
      target_id
    FROM
      (
        SELECT
          target_id
        FROM
          target_merge_dist final
        where
          (
            '2026-03-31 15:00:00' >= created_time
            and (
              deleted_time = = 0
              or deleted_time >= '2026-03-30 15:00:00'
            )
          )
          AND target_kind = 'application'
          AND arrayExists (
            x -> x IN ('27c5ce4d-b265-4d23-88cd-3ef1dce6dd49'),
            relation_targets['application_group']
          )
      )
  )
  AND collect_time = '2026-03-31 04:28:00'
ORDER BY
  elapsed_time DESC
limit
  1000 SETTINGS max_execution_time = 60
  /*-------------------------------------------------------------------------------------------
  com.exem.one.api.meta.v6.tag.persistence.mapper.TargetTagMapper.selectTargetInfoByIdAndTime
  -------------------------------------------------------------------------------------------*/
  /* exemONE : selectTargetInfoByIdAndTime */
SELECT distinct
  target_id as id,
  target_kind as category,
  sub_kind as c_category,
  system_attributes['origin_name'] as name,
  system_attributes['alias'] as alias
FROM
  target_merge_dist
WHERE
  target_kind = 'application'
  and target_id in (
    SELECT DISTINCT
      target_id
    FROM
      (
        SELECT
          target_id
        FROM
          target_merge_dist final
        where
          (
            '2026-03-31 15:00:00' >= created_time
            and (
              deleted_time = = 0
              or deleted_time >= '2026-03-30 15:00:00'
            )
          )
          AND target_kind = 'application'
          AND arrayExists (
            x -> x IN ('27c5ce4d-b265-4d23-88cd-3ef1dce6dd49'),
            relation_targets['application_group']
          )
      )
  )
  and toDateTime ('2026-03-31 15:00:00') >= created_time
  and (
    deleted_time = 0
    or deleted_time >= toDateTime ('2026-03-30 15:00:00')
  )