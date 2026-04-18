# user_library_ingestion_path_20260417 / main

- scope locked:
  - keep the existing customer-pack private runtime boundary and draft lifecycle
  - expose the normalized result as an explicit `User Library` product path in Control Tower
  - do not redesign the broader upload architecture or retrieval boundary in this packet
- validation target:
  - normalized uploaded books appear through a user-library contract in the data control room payload
  - Control Tower makes the upload result read as `saved to user library`
  - frontend build and focused Python UI/data tests succeed
- implementation notes:
  - `customer_pack_runtime_books` remains intact as the broader forensic/runtime bucket
  - new `user_library_books` is intentionally narrower and points only at uploaded source books in the private customer lane, not derived playbook families
  - `WorkspacePage` now shares the same accept-contract constant so Studio and Control Tower expose the same supported upload extensions
