# Registry Gate and Ordering Evidence

The observed lifecycle is:

`upstream success → Manifest complete → Registry register → Registry commit → EventEnvelope construction → EventEngine.process`

Registry output is only the successful-publication gate. The integration test
observed the committed row from a separate connection inside the Event Engine
handler, proving commit visibility before processing. Registry failure causes
zero envelope construction and zero Event Engine calls.
