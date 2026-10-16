
### 3. `database_schema.md`

```markdown
# Database Schema

## payments

| Column | Type | Nullable |
|---|---|---|
| payment_id | UUID | NO |
| order_id | VARCHAR | NO |
| transaction_id | VARCHAR | NO |
| amount | DECIMAL | NO |
| currency | VARCHAR | NO |
| status | VARCHAR | NO |
| created_at | TIMESTAMP | NO |

## Constraints

- `payment_id` must not be NULL.
- `order_id` must not be NULL.
- `transaction_id` must not be NULL.
- `amount` must not be NULL.
- `currency` must not be NULL.
- `status` must not be NULL.