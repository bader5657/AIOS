# Business and Dependency Separation

AIOS Core owns no customer, order, product, transaction, finance, admin,
Shoegabox, content, or other business behavior.

Direction remains Event Engine/integration boundary → AIOS Core → Brain
boundary. Core may depend only on the minimum active upstream contract selected
later. It may not depend on Brain runtime, Memory, Specialist Router, business
features, PostgreSQL implementation, Storage, Metadata, or Manifest internals.
