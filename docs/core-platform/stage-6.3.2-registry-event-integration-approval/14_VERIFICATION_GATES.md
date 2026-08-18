# Verification Gates

Implementation acceptance requires all of the following:

1. Universal Ingestion is the sole publisher; Registry/Engine/Pipeline/Manifest are not.
2. Registry commit precedes publication; Registry failure yields zero Process calls.
3. No DomainEvent yields zero Process calls and successful registration remains valid.
4. No synthetic or Registry-derived DomainEvent exists.
5. Exactly one supplied DomainEvent and one envelope per publication attempt.
6. Every active envelope field maps exactly as approved.
7. Envelope construction occurs outside Event Engine.
8. Exactly one directly awaited Process call; no retry or parallelism.
9. DomainEvent and EventEnvelope remain unchanged.
10. Success and all three existing failure codes map exactly; no new code.
11. Registry row, original, metadata, and Manifest survive Event Engine failure.
12. Registry transaction remains complete and local before Process.
13. No broker, persistence, config behavior, consumer, or Stage 5/Domain change.
14. Disposable PostgreSQL end-to-end evidence passes; production is untouched.
15. Stage 5, Stage 6.3.1, Domain, Core, compile/static, dependency, prohibited-source, and closed-world gates pass.
