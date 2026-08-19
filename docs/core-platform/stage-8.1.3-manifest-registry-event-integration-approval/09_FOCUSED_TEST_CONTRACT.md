# Focused Test Contract

The dedicated test must prove:

1. Manifest completion precedes the single Registry call;
2. exact `RegistryPersistenceInput` mapping and absence of direct RequestContext IDs;
3. a real Registry transaction commits before Event Engine processing;
4. a test handler can observe the committed row;
5. Registry failure prevents envelope construction and Event Engine processing;
6. Registry failure preserves original, metadata, and Manifest;
7. no DomainEvent produces successful registration and zero Event Engine calls;
8. a valid DomainEvent produces exactly one call with exact envelope mapping;
9. Registry record ID is absent from the envelope;
10. success, `NO_HANDLER`, and `HANDLER_FAILURE` mappings remain exact;
11. bounded and unexpected Event Engine failures preserve committed state;
12. there is no retry, deduplication, cross-component transaction, or AIOS Core call.

Use only local fakes/spies and fake asynchronous handlers around the accepted real
orchestration. Mocks may observe boundaries but must not replace the ordering being
proved.
