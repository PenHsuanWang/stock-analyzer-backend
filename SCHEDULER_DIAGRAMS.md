# Scheduler Module - Visual Architecture Diagrams

## 1. High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Existing System                              │
│                        (No Modifications)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │
│  │ YFinance     │      │ DataIOButler │      │ RedisAdapter │      │
│  │ Fetcher      │      │              │      │              │      │
│  └──────────────┘      └──────────────┘      └──────────────┘      │
│         ▲                      ▲                      ▲             │
│         │                      │                      │             │
│         │ uses (read-only)     │ uses                 │ uses        │
│         │                      │                      │             │
└─────────┼──────────────────────┼──────────────────────┼─────────────┘
          │                      │                      │
          │                      │                      │
┌─────────┼──────────────────────┼──────────────────────┼─────────────┐
│         │     New Scheduler Module (Extension)        │             │
│         │                      │                      │             │
├─────────┴──────────────────────┴──────────────────────┴─────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    Core Layer                               │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │     │
│  │  │ Scheduled    │  │     Job      │  │     Job      │     │     │
│  │  │   Job        │  │  Registry    │  │  Executor    │     │     │
│  │  │ (Data Model) │  │  (Storage)   │  │ (Execution)  │     │     │
│  │  └──────────────┘  └──────────────┘  └──────┬───────┘     │     │
│  │         │                   │                │             │     │
│  │         └───────────────────┴────────────────┘             │     │
│  │                             │                              │     │
│  │                    ┌────────▼─────────┐                    │     │
│  │                    │  Job Scheduler   │                    │     │
│  │                    │  (Coordination)  │                    │     │
│  │                    └──────────────────┘                    │     │
│  └────────────────────────────┬───────────────────────────────┘     │
│                               │                                     │
│  ┌────────────────────────────▼───────────────────────────────┐     │
│  │                    Webapp Layer                             │     │
│  │  ┌──────────────────────────────────────────────────┐      │     │
│  │  │        SchedulerServingApp (Singleton)           │      │     │
│  │  └──────────────────┬───────────────────────────────┘      │     │
│  │                     │                                       │     │
│  │  ┌──────────────────▼───────────────────────────────┐      │     │
│  │  │         FastAPI Router                           │      │     │
│  │  │  POST   /scheduler/jobs                          │      │     │
│  │  │  GET    /scheduler/jobs                          │      │     │
│  │  │  GET    /scheduler/jobs/{id}                     │      │     │
│  │  │  PUT    /scheduler/jobs/{id}                     │      │     │
│  │  │  DELETE /scheduler/jobs/{id}                     │      │     │
│  │  │  POST   /scheduler/jobs/{id}/start               │      │     │
│  │  │  POST   /scheduler/jobs/{id}/stop                │      │     │
│  │  │  GET    /scheduler/status                        │      │     │
│  │  └──────────────────────────────────────────────────┘      │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## 2. Detailed Class Relationships

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Class Relationship Diagram                       │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│   <<dataclass>>         │
│   ScheduledJob          │
├─────────────────────────┤
│ + job_id: str           │
│ + name: str             │
│ + stock_ids: List[str]  │
│ + schedule_time: str    │
│ + is_active: bool       │
│ + created_at: datetime  │
│ + last_run: datetime    │
│ + next_run: datetime    │
│ + status: JobStatus     │
│ + start_date: str       │
│ + end_date: str         │
│ + prefix: str           │
├─────────────────────────┤
│ + validate(): bool      │
│ + to_dict(): dict       │
│ + from_dict(): Self     │
└───────────┬─────────────┘
            │
            │ stored/retrieved by
            │
┌───────────▼─────────────┐
│   JobRegistry           │
├─────────────────────────┤
│ - adapter: AbstractDB   │
│ - _lock: Lock           │
│ - _job_key_prefix: str  │
│ - _job_index_key: str   │
├─────────────────────────┤
│ + create_job()          │
│ + get_job()             │
│ + list_jobs()           │
│ + update_job()          │
│ + delete_job()          │
│ + get_active_jobs()     │
│ - _add_to_index()       │
│ - _remove_from_index()  │
└───────────┬─────────────┘
            │
            │ uses
            │
┌───────────▼─────────────┐
│ AbstractDatabaseAdapter │  ← Existing Interface
├─────────────────────────┤
│ + save_data()           │
│ + get_data()            │
│ + exists()              │
│ + delete_data()         │
└─────────────────────────┘
            △
            │
            │ implemented by
            │
┌───────────┴─────────────┐
│    RedisAdapter         │  ← Existing Implementation
├─────────────────────────┤
│ - _redis_client         │
├─────────────────────────┤
│ + save_data()           │
│ + get_data()            │
│ + exists()              │
│ + delete_data()         │
└─────────────────────────┘


┌─────────────────────────┐
│   JobExecutor           │
├─────────────────────────┤
│ - _data_fetcher         │────────┐
│ - _data_butler          │───┐    │
│ - _execution_lock: Lock │   │    │
├─────────────────────────┤   │    │
│ + execute_job()         │   │    │
│ - _fetch_and_store()    │   │    │
│ - _handle_error()       │   │    │
└─────────────────────────┘   │    │
                              │    │
                    uses      │    │ uses
                              │    │
            ┌─────────────────┘    └──────────────────┐
            │                                         │
┌───────────▼─────────────┐         ┌─────────────────▼────────┐
│   DataIOButler          │         │   YFinanceFetcher        │
│   (Existing)            │         │   (Existing)             │
├─────────────────────────┤         ├──────────────────────────┤
│ + save_data()           │         │ + fetch_from_source()    │
│ + get_data()            │         │ + get_as_dataframe()     │
│ + update_data()         │         └──────────────────────────┘
└─────────────────────────┘


┌─────────────────────────┐
│   JobScheduler          │
├─────────────────────────┤
│ - registry: JobRegistry │───────┐
│ - executor: JobExecutor │───┐   │
│ - _scheduler_thread     │   │   │
│ - _is_running: bool     │   │   │
│ - _stop_event: Event    │   │   │
│ - check_interval: int   │   │   │
├─────────────────────────┤   │   │
│ + start()               │   │   │
│ + stop()                │   │   │
│ + is_running()          │   │   │
│ - _scheduler_loop()     │   │   │
│ - _check_and_execute()  │───┼───┤
│ - _execute_job_async()  │   │   │
└─────────────────────────┘   │   │
            │                 │   │
            │ coordinates     │   │
            └─────────────────┴───┘


┌─────────────────────────┐
│ SchedulerServingApp     │
│    <<singleton>>        │
├─────────────────────────┤
│ - scheduler             │───────┐
│ - registry              │───┐   │
│ - executor              │   │   │
│ - _app_lock: Lock       │   │   │
├─────────────────────────┤   │   │
│ + create_job()          │   │   │
│ + get_job()             │   │   │
│ + list_jobs()           │   │   │
│ + update_job()          │   │   │
│ + delete_job()          │   │   │
│ + start_job()           │   │   │
│ + stop_job()            │   │   │
│ + get_scheduler_status()│   │   │
└───────────┬─────────────┘   │   │
            │                 │   │
            │ exposed via     │   │
            │                 │   │
┌───────────▼─────────────┐   │   │
│   FastAPI Router        │   │   │
├─────────────────────────┤   │   │
│ + create_job()          │───┼───┘
│ + list_jobs()           │───┘
│ + get_job()             │
│ + update_job()          │
│ + delete_job()          │
│ + start_job()           │
│ + stop_job()            │
│ + get_scheduler_status()│
└─────────────────────────┘
```

## 3. Sequence Diagram: Job Creation and Execution

```
User          Router          ServingApp       Registry        Scheduler       Executor       Fetcher
 │              │                │               │               │               │              │
 │ POST /jobs   │                │               │               │               │              │
 ├─────────────>│                │               │               │               │              │
 │              │ create_job()   │               │               │               │              │
 │              ├───────────────>│               │               │               │              │
 │              │                │ create_job()  │               │               │              │
 │              │                ├──────────────>│               │               │              │
 │              │                │               │ save to Redis │               │              │
 │              │                │               ├───────────────┤               │              │
 │              │                │               │<──────────────┤               │              │
 │              │                │<──────────────┤               │               │              │
 │              │<───────────────┤               │               │               │              │
 │<─────────────┤                │               │               │               │              │
 │   job_id     │                │               │               │               │              │
 │              │                │               │               │               │              │
 │              │                │               │ [Background Thread Running]   │              │
 │              │                │               │               │               │              │
 │              │                │               │               │ check jobs    │              │
 │              │                │               │<──────────────┤               │              │
 │              │                │               │ get_active()  │               │              │
 │              │                │               ├──────────────>│               │              │
 │              │                │               │<──────────────┤               │              │
 │              │                │               │               │               │              │
 │              │                │               │               │ [Time Match]  │              │
 │              │                │               │               │               │              │
 │              │                │               │               │ execute_job() │              │
 │              │                │               │               ├──────────────>│              │
 │              │                │               │               │               │ fetch()      │
 │              │                │               │               │               ├─────────────>│
 │              │                │               │               │               │<─────────────┤
 │              │                │               │               │               │  DataFrame   │
 │              │                │               │               │               │              │
 │              │                │               │               │               │ save_data()  │
 │              │                │               │               │               ├──────────────┐
 │              │                │               │               │               │              │
 │              │                │               │               │               │<─────────────┘
 │              │                │               │               │<──────────────┤              │
 │              │                │               │               │  result       │              │
 │              │                │               │ update_job()  │               │              │
 │              │                │               │<──────────────┤               │              │
 │              │                │               │ (last_run,    │               │              │
 │              │                │               │  next_run)    │               │              │
 │              │                │               │               │               │              │
```

## 4. Thread Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        Main Thread                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │               FastAPI Server                             │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │     │
│  │  │  Worker 1  │  │  Worker 2  │  │  Worker N  │         │     │
│  │  └────────────┘  └────────────┘  └────────────┘         │     │
│  │        │               │               │                 │     │
│  │        └───────────────┴───────────────┘                 │     │
│  │                        │                                 │     │
│  │            API Request Handling                          │     │
│  └────────────────────────┬─────────────────────────────────┘     │
│                           │                                       │
│                           │ creates/controls                      │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            │                                │
┌───────────▼─────────────┐    ┌─────────────▼──────────────┐
│  Scheduler Thread       │    │  Job Execution Thread Pool │
│  (Background Daemon)    │    │  (Dynamic, per job)        │
│                         │    │                            │
│  ┌───────────────────┐  │    │  ┌──────────────────────┐ │
│  │  Scheduler Loop   │  │    │  │  Job Execution 1     │ │
│  │                   │  │    │  │  (Thread)            │ │
│  │  Every 60 seconds │  │    │  └──────────────────────┘ │
│  │                   │  │    │                            │
│  │  1. Get active    │──┼────┼─>┌──────────────────────┐ │
│  │     jobs          │  │    │  │  Job Execution 2     │ │
│  │                   │  │    │  │  (Thread)            │ │
│  │  2. Check if due  │  │    │  └──────────────────────┘ │
│  │                   │  │    │                            │
│  │  3. Spawn thread  │──┼────┼─>┌──────────────────────┐ │
│  │     for execution │  │    │  │  Job Execution N     │ │
│  │                   │  │    │  │  (Thread)            │ │
│  │  4. Sleep         │  │    │  └──────────────────────┘ │
│  │                   │  │    │                            │
│  └───────────────────┘  │    └────────────────────────────┘
│                         │
│  State: is_running      │
│  Control: _stop_event   │
└─────────────────────────┘


Thread Safety Mechanisms:

1. JobRegistry._lock          → Protects Redis operations
2. JobScheduler._app_lock     → Protects singleton creation
3. JobExecutor._execution_lock → (Future use for concurrency control)
4. Threading.Event            → Graceful shutdown signal
```

## 5. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Flow                                    │
└─────────────────────────────────────────────────────────────────────┘

1. Job Creation Flow
────────────────────

   User Input          API Layer           Core Layer          Storage
      │                   │                    │                  │
      │  Job Config       │                    │                  │
      ├──────────────────>│                    │                  │
      │                   │  ScheduledJob      │                  │
      │                   ├───────────────────>│                  │
      │                   │                    │  JSON            │
      │                   │                    ├─────────────────>│
      │                   │                    │                  │ Redis
      │                   │  job_id            │                  │ Key: scheduler:job:{id}
      │<──────────────────┤<───────────────────┤                  │
      │                   │                    │                  │


2. Scheduled Execution Flow
──────────────────────────

   Scheduler          Registry           Executor           Fetcher         Storage
      │                  │                  │                  │               │
      │ Check Time       │                  │                  │               │
      ├─────────────────>│                  │                  │               │
      │  Get Active Jobs │                  │                  │               │
      │<─────────────────┤                  │                  │               │
      │                  │                  │                  │               │
      │ [Time Match]     │                  │                  │               │
      │                  │                  │                  │               │
      │ Execute Job      │                  │                  │               │
      ├─────────────────────────────────────>│                  │               │
      │                  │                  │  Fetch AAPL      │               │
      │                  │                  ├─────────────────>│               │
      │                  │                  │    DataFrame     │               │
      │                  │                  │<─────────────────┤               │
      │                  │                  │                  │               │
      │                  │                  │  Store Data      │               │
      │                  │                  ├────────────────────────────────>│
      │                  │                  │                  │               │ Redis
      │                  │                  │  Fetch MSFT      │               │ Key: scheduled_stock_data:
      │                  │                  ├─────────────────>│               │      AAPL:2025-09-21:
      │                  │                  │    DataFrame     │               │      2025-10-21
      │                  │                  │<─────────────────┤               │
      │                  │                  │                  │               │
      │                  │                  │  Store Data      │               │
      │                  │                  ├────────────────────────────────>│
      │                  │                  │                  │               │
      │  Result          │                  │                  │               │
      │<─────────────────────────────────────┤                  │               │
      │                  │                  │                  │               │
      │ Update Job       │                  │                  │               │
      ├─────────────────>│                  │                  │               │
      │  (last_run,      │                  │                  │               │
      │   next_run)      │                  │                  │               │
      │                  │                  │                  │               │


3. Data Storage Structure in Redis
──────────────────────────────────

   Redis Database
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                  │
   │  Scheduler Index:                                               │
   │  ┌────────────────────────────────────────────────────────┐     │
   │  │ Key: scheduler:job_index                               │     │
   │  │ Value: ["job-id-1", "job-id-2", "job-id-3"]           │     │
   │  └────────────────────────────────────────────────────────┘     │
   │                                                                  │
   │  Job Data:                                                      │
   │  ┌────────────────────────────────────────────────────────┐     │
   │  │ Key: scheduler:job:job-id-1                            │     │
   │  │ Value: {                                               │     │
   │  │   "job_id": "job-id-1",                                │     │
   │  │   "name": "Daily Tech Stocks",                         │     │
   │  │   "stock_ids": ["AAPL", "MSFT"],                       │     │
   │  │   "schedule_time": "17:00",                            │     │
   │  │   "is_active": true,                                   │     │
   │  │   "next_run": "2025-10-22T17:00:00",                   │     │
   │  │   ...                                                  │     │
   │  │ }                                                      │     │
   │  └────────────────────────────────────────────────────────┘     │
   │                                                                  │
   │  Fetched Stock Data (uses existing format):                     │
   │  ┌────────────────────────────────────────────────────────┐     │
   │  │ Key: scheduled_stock_data:AAPL:2025-09-21:2025-10-21   │     │
   │  │ Value: [                                               │     │
   │  │   {"Date": "2025-09-21", "Open": 150.0, ...},         │     │
   │  │   {"Date": "2025-09-22", "Open": 151.0, ...},         │     │
   │  │   ...                                                  │     │
   │  │ ]                                                      │     │
   │  └────────────────────────────────────────────────────────┘     │
   │                                                                  │
   └──────────────────────────────────────────────────────────────────┘
```

## 6. State Machine: Job Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│                      Job Status State Machine                     │
└──────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │   PENDING   │  ← Initial state
                    └──────┬──────┘
                           │
                           │ Scheduler triggers
                           │
                    ┌──────▼──────┐
             ┌──────┤   RUNNING   │
             │      └──────┬──────┘
             │             │
             │             │ Success
             │             │
    Failure  │      ┌──────▼──────┐       Next schedule
             │      │  COMPLETED  ├───────────────┐
             │      └─────────────┘               │
             │                                    │
      ┌──────▼──────┐                             │
      │   FAILED    │                             │
      └──────┬──────┘                             │
             │                                    │
             │ Next schedule                      │
             │                                    │
             └──────────────┬─────────────────────┘
                            │
                            │
                    ┌───────▼────────┐
                    │    PENDING     │  ← Ready for next run
                    └────────────────┘
                            │
                            │ User stops job
                            │
                    ┌───────▼────────┐
                    │     PAUSED     │  ← Inactive
                    └───────┬────────┘
                            │
                            │ User starts job
                            │
                    ┌───────▼────────┐
                    │    PENDING     │
                    └────────────────┘


Actions on States:

- PENDING   → Can be started, stopped, updated, deleted
- RUNNING   → Can be stopped (will complete current execution)
- COMPLETED → Automatically transitions to PENDING for next run
- FAILED    → Automatically transitions to PENDING for retry
- PAUSED    → Can be started, updated, deleted
```

## 7. Error Handling Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     Error Handling Strategy                       │
└──────────────────────────────────────────────────────────────────┘

Job Execution Errors:

┌─────────────────┐
│  Execute Job    │
└────────┬────────┘
         │
         │ For each stock in job.stock_ids
         │
    ┌────▼──────────────────────────────────────┐
    │  Fetch & Store Single Stock               │
    └────┬──────────────────────────────────────┘
         │
         ├─ Success → Add to fetched_stocks[]
         │
         ├─ Failure → Add to failed_stocks[]
         │            Add error to errors[]
         │            Continue with next stock
         │
         └─ Log error, don't stop entire job


Result Status Logic:

    if failed_stocks is empty:
        status = "success"
    else if fetched_stocks is not empty:
        status = "partial_success"  ← Some succeeded
    else:
        status = "failed"            ← All failed


Individual Stock Error Handling:

    YFinanceFetcher Error
           │
           ├→ Invalid stock ID        → Log, continue
           ├→ API timeout             → Log, continue
           ├→ Network error           → Log, continue
           └→ Data empty              → Log, continue

    DataIOButler Error
           │
           ├→ Redis connection failed → Log, continue
           ├→ Serialization error     → Log, continue
           └→ Storage error           → Log, continue


Scheduler-Level Error Handling:

    ┌──────────────────┐
    │ Scheduler Loop   │
    └────────┬─────────┘
             │
             │ try-except wrapper
             │
    ┌────────▼──────────────────────────┐
    │  _check_and_execute_jobs()        │
    └────────┬──────────────────────────┘
             │
             ├─ Error → Log error
             │         Continue loop
             │         Don't crash scheduler
             │
             └─ Sleep & Continue


Thread Safety Errors:

    Lock Timeout
         │
         └→ Log warning
            Retry on next cycle


No Cascading Failures:
- One job failure doesn't affect other jobs
- One stock failure doesn't affect other stocks in job
- Scheduler continues even if all jobs fail
```

## 8. Integration Points with Existing System

```
┌────────────────────────────────────────────────────────────────────┐
│            Integration with Existing Components                    │
└────────────────────────────────────────────────────────────────────┘

New Module                 Interface              Existing Component
──────────                 ─────────              ──────────────────

┌──────────────┐                                ┌──────────────────┐
│ JobExecutor  │──── fetch_from_source() ──────>│ YFinanceFetcher  │
│              │      get_as_dataframe()        │                  │
└──────────────┘                                └──────────────────┘
       │                                                △
       │                                                │
       │ No modifications required                     │ Read-only
       │ Just calls existing methods                   │ usage
       │                                                │
       └────── save_data(                              │
                 data=df,                               │
                 prefix="...",            ┌────────────┴──────────┐
                 stock_id="...",          │   DataIOButler        │
                 start_date="...",        │                       │
                 end_date="..."    ───────>│ + save_data()         │
               )                           │ + get_data()          │
                                           │ + update_data()       │
                                           └───────────┬───────────┘
                                                       │
                                                       │ uses
                                                       │
                                           ┌───────────▼───────────┐
                                           │  RedisAdapter         │
                                           │                       │
                                           │ + save_data()         │
                                           │ + get_data()          │
                                           └───────────────────────┘

Key Points:
-----------
1. JobExecutor is a WRAPPER, not a modifier
2. All existing components used AS-IS
3. No inheritance, pure composition
4. Follows Dependency Inversion Principle
5. Zero impact on existing functionality


Server.py Integration:
---------------------

  Existing:                          New Addition:
  --------                           -------------

  from webapp.router import          from webapp.router import
    data_fetcher_router,               scheduler_router  ← ADD
    data_manager_router,
    analyzer_router

  app.include_router(                app.include_router(
    data_fetcher_router.router         scheduler_router.router  ← ADD
  )                                  )


That's it! Only 2 lines added.
```

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Status:** Ready for Development

