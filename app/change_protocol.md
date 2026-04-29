# Paraphraser Backend System – Architecture & Roadmap

## 1. Overview

This system is a backend service for a SaaS paraphrasing application built using FastAPI and a Hugging Face Pegasus model (`tuner007/pegasus_paraphrase`).

The system is designed to:

* Process user text inputs and generate paraphrased outputs
* Enforce usage limits based on subscription plans
* Support scalable growth as user demand increases

---

## 2. Current Architecture (MVP)

### 2.1 Core Components

**1. API Layer (FastAPI)**

* Handles incoming HTTP requests
* Performs authentication (JWT-based)
* Enforces usage limits via `usage_guard`
* Calls the paraphrasing engine

**2. ML Inference Layer**

* Uses a preloaded Pegasus model
* Performs:

  * Tokenization
  * Chunking (to avoid token overflow)
  * Controlled text generation

**3. Billing & Usage Control**

* Plans defined in `plans.py`
* Monthly character quotas enforced
* Per-request limits enforced

---

### 2.2 Request Flow

1. User sends paraphrase request
2. JWT is validated
3. `usage_guard` checks:

   * Monthly usage
   * Per-request character limits
4. Text is:

   * Validated
   * Chunked into safe token sizes
5. Model processes each chunk
6. Results are combined and returned
7. Usage is updated

---

## 3. Key Constraints & Safeguards

To ensure system stability:

* **Max tokens per chunk:** set to 60 with the current model
* **Max input characters:** enforced per plan
* **Max chunks per request:** enforced per plan
* **Beam search reduced (default = 2)** to control compute cost

These safeguards prevent:

* Model crashes (token overflow)
* Memory exhaustion
* Abuse from large inputs

---

## 4. Plan Enforcement

**Proposed pricing plan**

Free: $0

Basic: $4.99

Pro: $14.99

Max: $24.99


### Enforcement Strategy

* Requests exceeding limits are rejected before processing
* Monthly usage is tracked per user
* Limits are tied directly to compute cost

---

## 5. Current Limitations

The MVP system has the following constraints:

### 5.1 Synchronous Processing

* Requests are handled immediately
* No background processing
* High latency under load

### 5.2 Single Instance Model

* One model instance per deployment
* No horizontal scaling
* Memory duplication if scaled naïvely

### 5.3 No Request Queue

* Concurrent requests compete for resources
* Risk of slowdowns and timeouts

### 5.4 No GPU Optimization

* Runs on CPU (or unoptimized GPU usage)
* No batching or advanced inference optimization

---

## 6. Planned System Improvements

### 6.1 Queues Implementation

**Goal:** Prevent request blocking and improve reliability

**Design:**

* Introduce Redis as a message broker
* Use Celery for background workers

**New Flow:**

1. API receives request
2. Request is queued
3. Worker processes paraphrasing
4. Result is returned asynchronously

**Benefits:**

* Prevents API blocking
* Handles concurrent users better
* Improves fault tolerance

---

### 6.2 Async Scaling

**Goal:** To handle increased traffic

**Approach:**

* Deploy multiple API instances
* Use a load balancer
* Separate API from ML processing

**Architecture Shift:**

* API becomes lightweight
* Workers will handle heavy load computation

**Benefits:**

* Improved throughput
* Better user experience under load
* Horizontal scalability

---

### 6.3 Implement GPU Optimization

**Goal:** To reduce latency and increase throughput

**Enhancements:**

**1. Half Precision (FP16)**

* Reduces memory usage
* Speeds up inference

**2. Request Batching**

* Multiple requests processed together
* Improves GPU efficiency

**3. Dedicated Model Service**

* Persistent GPU-bound service
* Avoids repeated model loading

**Benefits:**

* Faster responses
* Lower cost per request
* Better scalability for high usage

---

## 7. Development Phases

### Phase 1 (Current)

* Stable MVP
* Enforced limits
* Reliable deployment

### Phase 2

* Introduce queue system
* Improve concurrency handling

### Phase 3

* Scale API and workers independently
* Optimize infrastructure

### Phase 4

* GPU acceleration
* Advanced optimization (batching, caching)

---

## 9. Key Principles

* Control compute usage → ensures profitability
* Enforce limits early → prevents abuse
* Scale only when necessary → avoid overengineering
* Separate concerns → API vs ML vs billing

---

## 10. Summary

The system is currently a functional MVP with:

* Controlled ML inference
* Secure authentication
* Usage-based billing

Future updates will focus on:

* Scalability (queue + async processing)
* Performance (GPU optimization)
* Reliability (distributed architecture)

The design prioritizes gradual evolution from a simple system to a scalable SaaS platform.
