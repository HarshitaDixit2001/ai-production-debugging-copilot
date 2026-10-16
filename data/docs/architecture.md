# Payment System Architecture

## Request Flow

Client
→ Payment Controller
→ Payment Service
→ Payment Repository
→ PostgreSQL Database

## Payment Service

The Payment Service validates payment requests and creates payment records.

The transaction ID must be generated before the payment record is persisted.

## Error Handling

Database errors are propagated to the API layer and returned as HTTP 500 responses.

## Components

- Payment Controller
- Payment Service
- Payment Repository
- PostgreSQL Database