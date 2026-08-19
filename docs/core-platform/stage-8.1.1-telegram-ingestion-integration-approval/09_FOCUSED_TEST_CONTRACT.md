# Focused Integration Test Contract

The exact test path is
`tests/integration/core_platform/test_telegram_ingestion_request_context_integration.py`.
It must prove, with fakes/mocks and no network:

1. an eligible fake Update/Message is accepted and the original Message is
   delegated exactly once and by object identity;
2. the adapter never constructs RequestContext, while Universal Ingestion
   constructs it exactly once with matching user, chat, message, username, and
   unchanged text values;
3. Universal Ingestion, not the adapter, recognizes ordinary text, Web Link,
   approved YouTube URL, and media;
4. Registry, Event Engine, and AIOS Core are not called in focused evidence;
5. malformed update never calls ingestion;
6. unsupported, empty, download failure, and bounded ingestion failure never
   emit the generic success acknowledgement;
7. a ready bounded result may emit the existing receipt acknowledgement;
8. `/start` and `status` remain outside general ingestion;
9. the adapter never downloads/persists files; the fake Storage path owns the
   single retrieval/preservation call and `file_id` stays transport-only;
10. there is no retry and no media-group state/aggregation;
11. there is no real Telegram network, token requirement, Registry/Event/Core
    lifecycle execution, or production configuration use.
