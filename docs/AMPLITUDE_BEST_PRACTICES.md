# Amplitude Analytics - Best Practices Manual

> 📊 **Version**: 2.1.0
> 📅 **Last Updated**: 2026-01-07
> 🔗 **Related Issues**: #83 (Initial Setup), #217-#223 (Implementation Phases), #305 (Credit & Subscription Events)

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Event Naming Conventions](#event-naming-conventions)
3. [Event Properties Guidelines](#event-properties-guidelines)
4. [User Identity Management](#user-identity-management)
5. [Technical Implementation](#technical-implementation)
6. [Event Catalog](#event-catalog)
7. [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
8. [Code Examples](#code-examples)
9. [Testing & Debugging](#testing--debugging)
10. [Privacy & Compliance](#privacy--compliance)

---

## Introduction

Amplitude Analytics is integrated into the Real Astrology application to track user behavior and enable data-driven product decisions. This manual provides comprehensive guidelines for implementing event tracking consistently and effectively.

**Integration Status**:
- ✅ Backend: `apps/api/app/services/amplitude_service.py`
- ✅ Frontend: `apps/web/src/services/amplitude.ts`
- ✅ **Session Replay**: `@amplitude/plugin-session-replay-browser` (100% sample rate)
- ✅ **Fully Implemented**: ~80 events across 10 categories
- ✅ **Coverage**: Authentication, Charts, Session, Navigation, Premium, Content, Errors, Profile, Password Reset, Email Verification, Credits
- ✅ **Session Tracking**: Handled automatically by Amplitude SDK (`defaultTracking.sessions: true`)

**Key Principles**:
1. **Consistency**: Use standardized naming and property formats
2. **Privacy**: Never send PII beyond user_id
3. **Quality**: Validate data before sending
4. **Performance**: Use async/non-blocking calls
5. **Documentation**: Document all events in this catalog

---

## Event Naming Conventions

### Standard Format

**Pattern**: `{object}_{action}` in `snake_case`

**Examples**:
- ✅ `user_registered`
- ✅ `chart_created`
- ✅ `subscription_upgraded`
- ✅ `password_reset_completed`

**NOT**:
- ❌ `userRegistered` (camelCase)
- ❌ `User Registered` (spaces, Title Case)
- ❌ `REGISTRATION` (all caps, unclear action)
- ❌ `new_user` (unclear action)

### Verb Tenses

Use **past tense** for completed actions:
- ✅ `user_logged_in` (not `user_login`)
- ✅ `chart_created` (not `chart_create`)
- ✅ `interpretation_generated` (not `interpretation_generate`)

Use **present continuous** for ongoing actions:
- ✅ `interpretation_generation_started`
- ✅ `chart_creation_submitted`

### Object Naming

Common objects in our application:
- `user` - User account actions
- `chart` - Birth chart operations
- `interpretation` - AI interpretation actions
- `subscription` - Premium subscription events
- `profile` - User profile management
- `oauth` - OAuth authentication
- `password_reset` - Password reset flow
- `email_verification` - Email verification flow
- `public_chart` - Famous/public charts
- `blog_post` - Blog content
- `rag_document` - RAG knowledge base

### Action Naming

Common actions:
- `created`, `updated`, `deleted` - CRUD operations
- `viewed`, `clicked` - User interactions
- `started`, `completed`, `failed` - Process states
- `requested`, `sent` - Request/response
- `searched`, `filtered`, `sorted` - Data operations
- `upgraded`, `downgraded`, `cancelled` - Subscription changes

---

## Event Properties Guidelines

### Property Naming

**Pattern**: `snake_case` for all property names

**Examples**:
```typescript
{
  house_system: "placidus",
  has_interpretations: true,
  error_type: "validation_error",
  generation_time_ms: 1250
}
```

**NOT**:
```typescript
{
  houseSystem: "placidus",        // ❌ camelCase
  "Has Interpretations": true,    // ❌ spaces
  ErrorType: "validation_error",  // ❌ PascalCase
  generationTimeMS: 1250          // ❌ camelCase with acronym
}
```

### Data Types

Use appropriate data types for properties:

| Type | Use For | Example |
|------|---------|---------|
| `string` | Categories, identifiers, text | `"placidus"`, `"google"` |
| `number` | Counts, durations, amounts | `42`, `1250`, `29.99` |
| `boolean` | True/false flags | `true`, `false` |
| `string[]` | Lists of items | `["full_name", "timezone"]` |

**Examples**:
```typescript
// ✅ Good
{
  chart_count: 5,                    // number
  has_interpretations: true,          // boolean
  house_system: "placidus",          // string
  fields_changed: ["email", "name"]  // string[]
}

// ❌ Bad
{
  chart_count: "5",                  // should be number
  has_interpretations: "true",       // should be boolean
  house_system: 1,                   // should be string
  fields_changed: "email, name"      // should be array
}
```

### Property Value Limits

**String Properties**:
- Maximum length: **1000 characters**
- Longer strings will be truncated automatically
- Use concise, meaningful values

**Array Properties**:
- Maximum items: **50** (recommended)
- Each item subject to string length limits
- Use only for genuinely multi-valued properties

**Number Properties**:
- Use integers for counts: `chart_count: 5`
- Use milliseconds for durations: `generation_time_ms: 1250`
- Use cents for currency: `amount_cents: 2999` (not `amount: 29.99`)

### Required vs Optional Properties

**Every event should include** (when applicable):
- `method` - How the action was performed (e.g., `"email_password"`, `"google_oauth"`)
- `source` - **Where the action originated** (e.g., `"dashboard"`, `"chart_detail"`, `"profile"`, `"landing"`)
  - ⚠️ **CRITICAL**: Always include `source` when tracking page views or actions that can be triggered from multiple locations
  - This allows us to understand user navigation patterns and which entry points are most effective
  - **Example**: A "Create Chart" button exists on Dashboard, Charts List, and Landing - use `source` to distinguish them
- `error_type` - Type of error for failed events (e.g., `"validation_error"`, `"api_error"`)

**Common optional properties**:
- `chart_id` - Specific chart reference
- `session_duration_minutes` - Session length
- `feature_name` - Feature identifier
- `generation_time_ms` - Processing time
- `used_cache` - Whether cached data was used

### Sensitive Data Handling

**NEVER send these as properties**:
- ❌ Passwords or password hashes
- ❌ API keys or tokens
- ❌ Credit card numbers
- ❌ Full birth dates (use age instead)
- ❌ Exact locations (use city/region)
- ❌ Phone numbers
- ❌ IP addresses (unless required for fraud detection)

**What you CAN send**:
- ✅ User ID (UUID)
- ✅ Email (for user identification only)
- ✅ Full name (for user properties)
- ✅ Generic location (city, country)
- ✅ Email verification status
- ✅ Subscription plan type

---

## User Identity Management

### When to Call `identify()`

Call `identify()` when:
1. **User logs in** (email/password or OAuth)
2. **User registers** (after successful registration)
3. **User properties change** (profile update, email verified)
4. **Session restoration** (user returns with valid token)

**DO NOT call identify()** on every page load - only when user properties change.

### User Properties to Set

**Recommended user properties**:
```typescript
{
  email: string,              // User's email (required)
  full_name: string,          // User's full name
  email_verified: boolean,    // Email verification status
  role: string,               // "free" | "premium" | "admin"
  user_type: string,          // "professional" | "student" | "curious"
  locale: string,             // "en-US" | "pt-BR"
  timezone: string,           // IANA timezone
  account_age_days: number,   // Days since registration
  total_charts: number,       // Total charts created
  has_subscription: boolean   // Premium subscription status
}
```

**Example**:
```typescript
// Frontend
amplitudeService.identify(user.id, {
  email: user.email,
  full_name: user.full_name,
  email_verified: user.email_verified,
  role: user.role,
});

// Backend
amplitude_service.identify(
    user_id=str(user.id),
    user_properties={
        "email": user.email,
        "full_name": user.full_name,
        "email_verified": user.email_verified,
        "role": user.role,
    },
)
```

### When to Call `reset()`

Call `reset()` when:
1. **User logs out** (explicit logout action)
2. **Session expired** (token invalidated)
3. **User switches accounts** (before identifying new user)

**Example**:
```typescript
// Frontend - in logout handler
const logout = () => {
  amplitudeService.reset();
  clearTokens();
  setUser(null);
};
```

### When to Call `track()`

Call `track()` for **every significant user action**:
- User interactions (clicks, form submissions)
- State changes (creation, update, deletion)
- Process milestones (started, completed, failed)
- Navigation events (page views, section changes)

**Example**:
```typescript
// After successful chart creation
amplitudeService.track('chart_created', {
  house_system: 'placidus',
  has_name: true,
  location_type: 'geocoded',
});
```

---

## Technical Implementation

### Frontend vs Backend Strategy

| Event Type | Track Where | Rationale |
|-----------|-------------|-----------|
| **Page Views** | Frontend | Client-side navigation, instant feedback |
| **Button Clicks** | Frontend | UI interactions, no API dependency |
| **Form Start** | Frontend | Funnel analysis (drop-off points) |
| **Form Submit** | Both | Frontend: funnel, Backend: success/fail |
| **API Success** | Backend | Source of truth, accurate user_id |
| **API Errors** | Backend | Accurate error details, stack traces |
| **User Properties** | Backend | Consistent with database state |
| **Navigation** | Frontend | Client-side routing (React Router) |
| **UI Errors** | Frontend | Component errors, rendering issues |

### Frontend Implementation

**Location**: `apps/web/src/services/amplitude.ts`

**Service Methods**:
```typescript
class AmplitudeService {
  track(eventName: string, properties?: Record<string, any>): void
  identify(userId: string, userProperties?: Record<string, any>): void
  reset(): void
  flush(): Promise<void>
}
```

**Where to Add Tracking**:
1. **Page Components** - Page views on mount
2. **Event Handlers** - User interactions (onClick, onSubmit)
3. **useEffect Hooks** - Side effects, state changes
4. **Error Boundaries** - Component errors
5. **AuthContext** - Authentication events (already implemented)

**Example - Page View Tracking**:
```typescript
// In page component
useEffect(() => {
  amplitudeService.track('page_viewed', {
    page_path: location.pathname,
    page_title: 'Chart Detail',
  });
}, [location.pathname]);
```

**Example - Button Click Tracking**:
```typescript
const handleCreateChart = () => {
  amplitudeService.track('chart_creation_started', {
    source: 'dashboard',
  });
  navigate('/charts/new');
};
```

### Session Replay Integration

**Status**: ✅ Implemented

Amplitude Session Replay captures user sessions for debugging and UX analysis.

**Configuration**:
```bash
# apps/web/.env
VITE_SESSION_REPLAY_SAMPLE_RATE=1  # 0.0 to 1.0 (default: 1.0 = 100%)
```

**How It Works**:
1. Session Replay plugin is added before Amplitude initialization
2. All user interactions are recorded (clicks, scrolls, form inputs)
3. Recordings are viewable in Amplitude's Session Replay dashboard
4. Sample rate controls percentage of sessions recorded (1.0 = 100%)

**Privacy Considerations**:
- Session Replay automatically masks sensitive inputs (passwords, credit cards)
- Email fields and other PII are masked by default
- Review recordings to ensure no sensitive data is exposed

**Accessing Recordings**:
1. Go to Amplitude Dashboard → Session Replay
2. Filter by user_id, event, or time range
3. Watch recordings to debug issues or analyze UX

### Backend Implementation

**Location**: `apps/api/app/services/amplitude_service.py`

**Service Methods**:
```python
class AmplitudeService:
    def track(
        self,
        event_type: str,
        user_id: str | None = None,
        device_id: str | None = None,
        event_properties: dict | None = None,
    ) -> None

    def identify(
        self,
        user_id: str,
        user_properties: dict | None = None,
    ) -> None

    def flush(self) -> None
```

**Where to Add Tracking**:
1. **API Endpoints** - After successful operations
2. **Exception Handlers** - Error events
3. **Background Tasks** - Async operations (Celery)
4. **Middleware** - Request/response tracking
5. **Services** - Business logic milestones

**Example - Endpoint Tracking**:
```python
@router.post("/charts", response_model=ChartRead)
async def create_chart(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Create chart
        chart = await chart_service.create_chart(db, chart_data, current_user.id)

        # Track success
        amplitude_service.track(
            event_type="chart_created",
            user_id=str(current_user.id),
            event_properties={
                "house_system": chart_data.house_system,
                "has_name": bool(chart_data.person_name),
                "location_type": "geocoded",
            },
        )

        return chart
    except Exception as e:
        # Track failure
        amplitude_service.track(
            event_type="chart_creation_failed",
            user_id=str(current_user.id),
            event_properties={
                "error_type": type(e).__name__,
                "error_message": str(e)[:100],  # Truncate
            },
        )
        raise
```

### Error Handling

**Always wrap tracking in try-except** to prevent tracking failures from breaking the application:

**Frontend**:
```typescript
try {
  amplitudeService.track('chart_created', properties);
} catch (error) {
  console.error('Amplitude tracking failed:', error);
  // Don't throw - tracking is non-critical
}
```

**Backend** (handled automatically by service):
```python
# Service handles errors internally
try:
    self.client.track(event)
    logger.debug(f"Amplitude event tracked: {event_type}")
except Exception as e:
    logger.error(f"Failed to track Amplitude event '{event_type}': {e}")
    # Never raise - tracking failures should not break the app
```

### Performance Considerations

**Frontend**:
- Amplitude SDK batches events automatically
- Events sent asynchronously (non-blocking)
- Use `flush()` only when absolutely necessary (e.g., before page unload)

**Backend**:
- Events sent asynchronously via HTTP client
- No performance impact on API responses
- Batch events in background tasks when possible

**Example - Batch Tracking**:
```python
# In Celery task
@celery_app.task
def process_bulk_operation(user_id: str, items: list):
    for item in items:
        # Process item
        result = process_item(item)

        # Track each item (batched by SDK)
        amplitude_service.track(
            event_type="item_processed",
            user_id=user_id,
            event_properties={"item_id": item.id, "status": result.status},
        )

    # Flush at the end to ensure all events are sent
    amplitude_service.flush()
```

---

## Event Catalog

### Currently Implemented Events

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `user_registered` | Backend: `auth.py:63`<br>Frontend: `AuthContext.tsx:137` | `method`, `accept_terms` | User completes registration |
| `user_logged_in` | Backend: `auth.py:126`<br>Frontend: `AuthContext.tsx:111` | `method` | User logs in successfully |
| User identity reset | Frontend: `AuthContext.tsx:52` | - | User logs out |

**Event Details**:

#### `user_registered`
**Description**: User successfully completed registration.

**Properties**:
- `method` (string): Authentication method (`"email_password"`)
- `accept_terms` (boolean): Whether user accepted terms of service

**Tracked**:
- ✅ Backend: After user created in database
- ✅ Frontend: Before auto-login (funnel tracking)

**Example**:
```typescript
amplitudeService.track('user_registered', {
  method: 'email_password',
  accept_terms: true,
});
```

#### `user_logged_in`
**Description**: User successfully logged in.

**Properties**:
- `method` (string): Login method (`"email_password"`, `"google_oauth"`, `"github_oauth"`, `"facebook_oauth"`)

**Tracked**:
- ✅ Backend: After token generated
- ✅ Frontend: After user fetched from API

**User Properties Set**:
- `email` (string)
- `full_name` (string)
- `email_verified` (boolean)

**Example**:
```typescript
amplitudeService.identify(user.id, {
  email: user.email,
  full_name: user.full_name,
  email_verified: user.email_verified,
});
amplitudeService.track('user_logged_in', {
  method: 'email_password',
});
```

### Authentication Events (Issues #218, #219)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `user_registered` | Backend: `auth.py`, `oauth.py`<br>Frontend: `AuthContext.tsx` | `method`, `accept_terms`, `source` | User completes registration |
| `user_logged_in` | Backend: `auth.py`, `oauth.py`<br>Frontend: `AuthContext.tsx` | `method`, `source` | User logs in successfully |
| `oauth_login_initiated` | Frontend: `Login.tsx`, `Register.tsx` | `provider`, `source` | User clicks OAuth button |
| `oauth_login_completed` | Frontend: `OAuthCallback.tsx` | `provider`, `source` | OAuth login succeeds |
| `oauth_login_failed` | Frontend: `OAuthCallback.tsx`<br>Backend: `oauth.py` | `provider`, `error_type`, `error_message`, `source` | OAuth login fails |
| `oauth_connection_added` | Backend: `oauth.py` | `provider`, `source` | OAuth linked to existing account |
| `login_form_submitted` | Frontend: `Login.tsx` | `source` | User submits login form |
| `login_failed` | Frontend: `Login.tsx` | `error_type`, `error_message`, `source` | Login attempt fails |
| `registration_form_submitted` | Frontend: `Register.tsx` | `accept_terms`, `source` | User submits registration form |
| `registration_failed` | Frontend: `Register.tsx` | `error_type`, `error_message`, `source` | Registration attempt fails |

**Event Details**:

#### `oauth_login_initiated`
**Description**: User clicks an OAuth provider button to start authentication.

**Properties**:
- `provider` (string): OAuth provider (`"google"`, `"github"`, `"facebook"`)
- `source` (string): Page where initiated (`"login"`, `"register"`)

**Example**:
```typescript
amplitudeService.track('oauth_login_initiated', {
  provider: 'google',
  source: 'login',
});
```

#### `login_form_submitted`
**Description**: User submits the email/password login form (tracks funnel before success/failure).

**Properties**:
- `source` (string): Always `"login_page"`

**Example**:
```typescript
amplitudeService.track('login_form_submitted', {
  source: 'login_page',
});
```

#### `login_failed`
**Description**: Email/password login attempt failed.

**Properties**:
- `error_type` (string): Type of error (`"invalid_credentials"`, `"network_error"`)
- `error_message` (string): Error message (truncated, max 100 chars)
- `source` (string): Always `"login_page"`

### Email Verification Events (Issue #219)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `email_verification_attempted` | Frontend: `VerifyEmailPage.tsx` | `source` | User accesses verification link |
| `email_verified` | Frontend: `VerifyEmailPage.tsx`<br>Backend: `auth.py` | `method`, `source` | Email verification succeeds |
| `email_verification_failed` | Frontend: `VerifyEmailPage.tsx`<br>Backend: `auth.py` | `error_type`, `error_message`, `source` | Email verification fails |
| `verification_email_resent` | Backend: `auth.py` | `source` | User requests new verification email |
| `verification_email_resend_failed` | Backend: `auth.py` | `error_type`, `error_message`, `source` | Resend verification fails |

**Event Details**:

#### `email_verification_attempted`
**Description**: User clicks the email verification link and lands on the verification page.

**Properties**:
- `source` (string): Always `"email_link"`

**Example**:
```typescript
amplitudeService.track('email_verification_attempted', {
  source: 'email_link',
});
```

#### `email_verified`
**Description**: Email verification completed successfully.

**Properties**:
- `method` (string): Verification method (`"email_link"`)
- `source` (string): Source of the event (`"verify_page"`, `"api"`)

#### `verification_email_resent`
**Description**: User successfully requested a new verification email.

**Properties**:
- `source` (string): Always `"api"`

### Password Reset Events (Issue #219)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `password_reset_requested` | Frontend: `ForgotPassword.tsx` | `source` | User submits forgot password form |
| `password_reset_email_sent` | Frontend: `ForgotPassword.tsx`<br>Backend: `password_reset.py` | `method`, `source` | Reset email sent successfully |
| `password_reset_link_accessed` | Frontend: `ResetPassword.tsx` | `source` | User clicks reset link in email |
| `password_reset_form_submitted` | Frontend: `ResetPassword.tsx` | `source` | User submits new password |
| `password_reset_completed` | Frontend: `ResetPassword.tsx`<br>Backend: `password_reset.py` | `method`, `source` | Password successfully reset |
| `password_reset_failed` | Frontend: `ResetPassword.tsx`, `ForgotPassword.tsx`<br>Backend: `password_reset.py` | `error_type`, `error_message`, `source` | Password reset fails at any stage |

**Event Details**:

#### `password_reset_requested`
**Description**: User initiates password reset by submitting their email.

**Properties**:
- `source` (string): Always `"forgot_password_page"`

**Example**:
```typescript
amplitudeService.track('password_reset_requested', {
  source: 'forgot_password_page',
});
```

#### `password_reset_completed`
**Description**: User successfully sets a new password.

**Properties**:
- `method` (string): Reset method (`"email_link"`)
- `source` (string): Source of the event (`"reset_page"`, `"api"`)

### Chart Events (Issues #218, #219)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `chart_list_viewed` | Frontend: `Charts.tsx` | `chart_count`, `source` | User views charts list page |
| `chart_detail_viewed` | Frontend: `ChartDetail.tsx` | `chart_id`, `has_interpretation`, `source` | User views a chart |
| `chart_creation_started` | Frontend: `NewChart.tsx` | `source` | User navigates to create chart page |
| `chart_location_searched` | Frontend: `NewChart.tsx` | `query`, `results_count` | User searches for birth location |
| `chart_location_selected` | Frontend: `NewChart.tsx` | `location_type`, `has_timezone` | User selects a location |
| `chart_creation_submitted` | Frontend: `NewChart.tsx` | `house_system`, `has_name`, `source` | User submits chart creation form |
| `chart_created` | Frontend: `NewChart.tsx` | `chart_id`, `house_system`, `has_name`, `source` | Chart created successfully |
| `chart_creation_failed` | Frontend: `NewChart.tsx` | `error_type`, `error_message`, `source` | Chart creation fails |
| `chart_deleted` | Frontend: `Charts.tsx` | `chart_id`, `source` | User deletes a chart |
| `chart_deletion_cancelled` | Frontend: `Charts.tsx` | `chart_id`, `source` | User cancels chart deletion |
| `interpretation_generation_started` | Frontend: `ChartDetail.tsx` | `chart_id`, `source` | User requests AI interpretation |
| `interpretation_generated` | Frontend: `ChartDetail.tsx` | `chart_id`, `generation_time_ms`, `source` | AI interpretation completed |
| `interpretation_generation_failed` | Frontend: `ChartDetail.tsx` | `chart_id`, `error_type`, `error_message`, `source` | AI interpretation fails |

**Event Details**:

#### `chart_list_viewed`
**Description**: User views their charts list page.

**Properties**:
- `chart_count` (number): Number of charts user has
- `source` (string): Always `"charts_page"`

**Example**:
```typescript
amplitudeService.track('chart_list_viewed', {
  chart_count: 5,
  source: 'charts_page',
});
```

#### `chart_location_searched`
**Description**: User searches for a birth location during chart creation.

**Properties**:
- `query` (string): Search query (truncated to 50 chars)
- `results_count` (number): Number of results returned

#### `chart_created`
**Description**: Birth chart created successfully.

**Properties**:
- `chart_id` (string): UUID of the created chart
- `house_system` (string): House system used (`"placidus"`, `"koch"`, etc.)
- `has_name` (boolean): Whether person's name was provided
- `source` (string): Always `"new_chart_page"`

#### `interpretation_generated`
**Description**: AI interpretation generated successfully.

**Properties**:
- `chart_id` (string): UUID of the chart
- `generation_time_ms` (number): Time taken in milliseconds
- `source` (string): Always `"chart_detail_page"`

### Profile/Account Events (Issue #219)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `profile_viewed` | Frontend: `Profile.tsx` | `source` | User views profile page |
| `profile_updated` | Backend: `users.py` | `fields_changed`, `source` | User updates profile info |
| `profile_password_changed` | Backend: `users.py` | `source` | User changes password |
| `profile_password_change_failed` | Backend: `users.py` | `error_type`, `source` | Password change fails |
| `oauth_connection_removed` | Backend: `users.py` | `provider`, `source` | User disconnects OAuth provider |
| `account_deletion_requested` | Backend: `users.py`, `privacy.py` | `has_charts`, `chart_count`, `source` | User requests account deletion |
| `account_deletion_cancelled` | Backend: `privacy.py` | `source` | User cancels pending deletion |
| `account_deleted` | Backend: `privacy.py` | `had_charts`, `chart_count`, `source` | Account hard deleted (30 days later) |

**Event Details**:

#### `profile_viewed`
**Description**: User views their profile settings page.

**Properties**:
- `source` (string): Always `"profile_page"`

#### `profile_updated`
**Description**: User updates their profile information.

**Properties**:
- `fields_changed` (string[]): List of updated fields (`["full_name", "timezone"]`)
- `source` (string): Always `"api"`

**Example**:
```python
amplitude_service.track(
    event_type="profile_updated",
    user_id=str(user.id),
    event_properties={
        "fields_changed": ["full_name", "timezone"],
        "source": "api",
    },
)
```

#### `account_deletion_requested`
**Description**: User initiates account deletion (soft delete, 30-day retention).

**Properties**:
- `has_charts` (boolean): Whether user has any charts
- `chart_count` (number): Number of charts to be deleted
- `source` (string): Source of request (`"profile_page"`, `"privacy_page"`)

#### `account_deleted`
**Description**: Account permanently deleted after 30-day retention period.

**Properties**:
- `had_charts` (boolean): Whether user had charts
- `chart_count` (number): Number of charts deleted
- `source` (string): Always `"celery_cleanup_task"`

### System Events

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `page_viewed` | Frontend: `useAmplitudePageView.ts` | `page_path`, `page_title`, `source` | User navigates to any page |

**Event Details**:

#### `page_viewed`
**Description**: Generic page view event for navigation tracking.

**Properties**:
- `page_path` (string): Current page path (e.g., `/charts`, `/profile`)
- `page_title` (string): Page title or identifier
- `source` (string): Navigation source if applicable

**Usage**:
```typescript
import { useAmplitudePageView } from '@/hooks/useAmplitudePageView';

function MyPage() {
  useAmplitudePageView('My Page Title');
  return <div>...</div>;
}
```

### Premium/Subscription Events (Issue #220, #305)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `pricing_page_viewed` | Frontend: `Pricing.tsx` | `source`, `user_tier` | User views pricing page |
| `pricing_plan_clicked` | Frontend: `Pricing.tsx` | `plan_name`, `current_tier`, `billing_cycle`, `source` | User clicks plan button |
| `premium_feature_blocked` | Frontend: `PremiumFeatureGate.tsx` | `feature_name`, `source` | Free user hits premium gate |
| `premium_upsell_clicked` | Frontend: `PremiumUpsell.tsx` | `feature_name`, `source` | User clicks upgrade link |
| `subscription_granted` | Backend: `subscription_service.py` | `days`, `is_lifetime`, `granted_by_admin_id`, `source` | Admin grants premium |
| `subscription_extended` | Backend: `subscription_service.py` | `extend_days`, `previous_expires_at`, `new_expires_at`, `source` | Admin extends subscription |
| `subscription_revoked` | Backend: `subscription_service.py` | `was_active`, `days_remaining`, `revoked_by_admin_id`, `source` | Admin revokes subscription |
| `subscription_expired` | Backend: `subscription_service.py` | `expired_at`, `source` | System auto-expires subscription |
| `subscription_renewed` | Backend: `stripe_webhook_handler.py` | `plan_type`, `amount`, `currency`, `stripe_subscription_id`, `source` | Subscription auto-renews via Stripe |

### Credit Events (Issue #305)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `credits_allocated` | Backend: `credit_service.py` | `plan_type`, `credits_allocated`, `is_unlimited`, `source` | Credits allocated on plan change |
| `credits_consumed` | Backend: `credit_service.py` | `feature_type`, `credits_consumed`, `balance_after`, `plan_type` | Credits consumed for a feature |
| `insufficient_credits` | Backend: `credit_service.py` | `feature_type`, `required`, `available`, `plan_type` | User attempts action without enough credits |
| `bonus_credits_added` | Backend: `credit_service.py` | `amount`, `balance_after`, `added_by_admin_id`, `reason` | Admin adds bonus credits |
| `credits_reset` | Backend: `credit_service.py` | `plan_type`, `old_balance`, `new_balance`, `source` | Monthly credit reset |
| `credits_low_warning` | Backend: `credit_service.py` | `balance_remaining`, `credits_limit`, `threshold_percent`, `plan_type` | Credits drop below 20% threshold |
| `credits_refunded` | Backend: `credit_service.py` | `amount`, `balance_after`, `refunded_by_admin_id`, `reason`, `original_transaction_id` | Admin refunds credits |

**Event Details**:

#### `subscription_renewed`
**Description**: Subscription auto-renewed via Stripe webhook when billing cycle completes.

**Properties**:
- `plan_type` (string): Current plan type (`"starter"`, `"pro"`, `"unlimited"`)
- `amount` (number): Payment amount in cents
- `currency` (string): Currency code (`"brl"`)
- `stripe_subscription_id` (string): Stripe subscription ID
- `source` (string): Always `"stripe_webhook"`

#### `credits_low_warning`
**Description**: Tracked when user's credit balance drops below 20% of their plan limit (e.g., 2 credits remaining on a 10-credit plan).

**Properties**:
- `balance_remaining` (number): Credits remaining after consumption
- `credits_limit` (number): Total credits limit for the plan
- `threshold_percent` (number): Warning threshold percentage (20)
- `plan_type` (string): User's plan type

**Note**: Only tracked once when crossing the threshold, not on every consumption below threshold.

#### `credits_refunded`
**Description**: Admin refunds credits to a user (e.g., for service issues or goodwill).

**Properties**:
- `amount` (number): Credits refunded
- `balance_after` (number): New credit balance
- `refunded_by_admin_id` (string): Admin UUID who performed refund
- `reason` (string): Reason for refund
- `original_transaction_id` (string | null): ID of original transaction if applicable

**Event Details**:

#### `pricing_page_viewed`
**Description**: User views the pricing/plans page.

**Properties**:
- `source` (string): Where user came from (`"direct"`, `"navbar"`, `"upsell"`, `"feature_gate"`)
- `user_tier` (string): User's current tier (`"anonymous"`, `"free"`, `"premium"`, `"admin"`)

**Example**:
```typescript
amplitudeService.track('pricing_page_viewed', {
  source: 'upsell',
  user_tier: 'free',
});
```

#### `premium_feature_blocked`
**Description**: Free user attempts to access a premium-only feature.

**Properties**:
- `feature_name` (string): Feature attempted (`"horary"`, `"profections"`, `"firdaria"`, `"solar_returns"`)
- `source` (string): Page path where blocked

**Example**:
```typescript
amplitudeService.track('premium_feature_blocked', {
  feature_name: 'horary',
  source: '/chart/123',
});
```

#### `subscription_granted`
**Description**: Admin grants premium subscription to a user.

**Properties**:
- `days` (number | null): Days granted (null = lifetime)
- `is_lifetime` (boolean): Whether lifetime subscription
- `granted_by_admin_id` (string): Admin UUID
- `source` (string): `"admin_panel"`

**Example**:
```python
amplitude_service.track(
    event_type="subscription_granted",
    user_id=str(user_id),
    event_properties={
        "days": 30,
        "is_lifetime": False,
        "granted_by_admin_id": str(admin_user.id),
        "source": "admin_panel",
    },
)
```

### Content & Engagement Events (Issue #221)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `blog_viewed` | Frontend: `Blog.tsx` | `source`, `post_count`, `category_filter`, `tag_filter` | User views blog list |
| `blog_post_clicked` | Frontend: `Blog.tsx` | `post_slug`, `post_title`, `source` | User clicks blog post card |
| `blog_post_viewed` | Frontend: `BlogPost.tsx` | `post_slug`, `post_title`, `reading_time`, `source` | User views blog post detail |
| `blog_post_read_completed` | Frontend: `BlogPost.tsx` | `post_slug`, `estimated_read_percentage`, `time_on_page_seconds` | User scrolls to 80%+ of article |
| `public_charts_viewed` | Frontend: `PublicCharts.tsx` | `source`, `chart_count`, `category_filter` | User views famous charts gallery |
| `public_chart_searched` | Frontend: `PublicCharts.tsx` | `query`, `results_count` | User searches famous charts |
| `public_chart_clicked` | Frontend: `PublicCharts.tsx` | `chart_slug`, `person_name`, `category` | User clicks famous chart card |
| `public_chart_detail_viewed` | Frontend: `PublicChartDetail.tsx` | `chart_slug`, `person_name`, `category`, `source` | User views famous chart detail |
| `rag_documents_viewed` | Frontend: `RagDocuments.tsx` | `source`, `document_count`, `filter_type` | User views RAG documents list |
| `rag_document_clicked` | Frontend: `RagDocuments.tsx` | `document_id`, `document_type`, `title` | User clicks RAG document card |

**Event Details**:

#### `blog_post_read_completed`
**Description**: User has scrolled to approximately 80% of the blog post content, indicating they've likely read most of the article.

**Properties**:
- `post_slug` (string): Blog post identifier
- `estimated_read_percentage` (number): Always 80 (threshold for tracking)
- `time_on_page_seconds` (number): Time spent on page before completion

**Implementation**:
Uses Intersection Observer API for performance-efficient scroll tracking:
```typescript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const timeOnPage = Math.floor((Date.now() - pageLoadTime.current) / 1000);
        amplitudeService.track('blog_post_read_completed', {
          post_slug: post.slug,
          estimated_read_percentage: 80,
          time_on_page_seconds: timeOnPage,
        });
      }
    });
  },
  { threshold: 0.5 }
);
```

#### `public_chart_searched`
**Description**: User searches for famous/public charts in the gallery.

**Properties**:
- `query` (string): Search query text
- `results_count` (number): Number of results returned

**Example**:
```typescript
amplitudeService.track('public_chart_searched', {
  query: 'einstein',
  results_count: 3,
});
```

### Error & Performance Monitoring Events (Issue #222)

| Event Name | Location | Properties | Triggered When |
|-----------|----------|-----------|----------------|
| `error_occurred` | Frontend: `ErrorBoundary.tsx`, `main.tsx` | `error_type`, `error_message`, `page_path`, `component_name`, `stack_trace_snippet`, `source` | React error boundary catch or global error handler |
| `api_request_failed` | Frontend: `api.ts` | `endpoint`, `method`, `status_code`, `error_message`, `source` | API call fails (non-401) |
| `slow_performance_detected` | Frontend: `usePerformanceMonitoring.ts` | `page_path`, `load_time_ms`, `threshold_ms`, `resource_type`, `source` | Page load exceeds 3 seconds |
| `rate_limit_hit` | Frontend: `api.ts` | `endpoint`, `limit_type`, `retry_after_seconds`, `source` | User receives 429 response |
| `feature_unavailable` | Various | `feature_name`, `error_message`, `source` | Feature/service temporarily down |

**Event Details**:

#### `error_occurred`
**Description**: Captures JavaScript runtime errors for monitoring application stability.

**Properties**:
- `error_type` (string): Type of error (`runtime`, `network`, `validation`)
- `error_message` (string): Sanitized error message (PII removed)
- `page_path` (string): Current page path
- `component_name` (string): React component where error occurred
- `stack_trace_snippet` (string): First 200 chars of stack trace (sanitized)
- `source` (string): Error source (`error_boundary`, `global_handler`, `unhandled_rejection`)

**Implementation**:
```typescript
// ErrorBoundary.tsx
componentDidCatch(error: Error, errorInfo: ErrorInfo) {
  amplitudeService.track('error_occurred', {
    error_type: 'runtime',
    error_message: sanitizeErrorMessage(error.message),
    page_path: window.location.pathname,
    component_name: extractComponentName(errorInfo.componentStack),
    stack_trace_snippet: sanitizeStackTrace(error.stack),
    source: 'error_boundary',
  });
}
```

#### `api_request_failed`
**Description**: Tracks API failures for monitoring backend health and user experience issues.

**Properties**:
- `endpoint` (string): API endpoint path
- `method` (string): HTTP method (GET, POST, PUT, DELETE)
- `status_code` (number): HTTP status code
- `error_message` (string): Sanitized error message
- `source` (string): Always `api_client`

**Example**:
```typescript
amplitudeService.track('api_request_failed', {
  endpoint: '/api/v1/charts',
  method: 'POST',
  status_code: 500,
  error_message: 'Internal server error',
  source: 'api_client',
});
```

#### `rate_limit_hit`
**Description**: Tracks when users hit rate limits to identify abuse or capacity issues.

**Properties**:
- `endpoint` (string): Rate-limited endpoint
- `limit_type` (string): Type of limit (`login`, `register`, `password_reset`, `geocoding`, `api`)
- `retry_after_seconds` (number): Seconds until retry allowed
- `source` (string): Always `api_client`

#### `slow_performance_detected`
**Description**: Tracks slow page loads to identify performance bottlenecks.

**Properties**:
- `page_path` (string): Page that loaded slowly
- `load_time_ms` (number): Actual load time in milliseconds
- `threshold_ms` (number): Threshold that was exceeded (default: 3000)
- `resource_type` (string): Type of resource (`page`)
- `source` (string): Page identifier

**Usage**:
```typescript
// In any page component
import { usePerformanceMonitoring } from '@/hooks';

function Dashboard() {
  usePerformanceMonitoring('dashboard');
  return <div>...</div>;
}
```

**PII Sanitization**:
All error messages are sanitized before tracking:
- Emails → `[EMAIL]`
- Bearer tokens → `Bearer [TOKEN]`
- JWT tokens → `[JWT_TOKEN]`
- Passwords → `password=[REDACTED]`
- UUIDs → `[UUID]`
- API keys → `[API_KEY]`

### Implementation Status

All planned events from Issue #218 have been implemented across Issues #219-#222:

| Phase | Issue | Status | Events |
|-------|-------|--------|--------|
| Phase 1 | #83 | ✅ Complete | `user_registered`, `user_logged_in` |
| Phase 2 | #219 | ✅ Complete | Authentication, Charts, Profile, Email Verification, Password Reset |
| Phase 3 | #220 | ✅ Complete | Premium/Subscription events |
| Phase 4 | #221 | ✅ Complete | Content & Engagement events |
| Phase 5 | #222 | ✅ Complete | Error & Performance monitoring |
| Phase 6 | #223 | ✅ Complete | Documentation & Event Catalog |

**Total Events Tracked**: ~70 events across 8 categories

---

## Common Pitfalls to Avoid

### 1. Inconsistent Event Names

**❌ Bad**:
```typescript
// Different naming for similar events
amplitudeService.track('userLogin');           // camelCase
amplitudeService.track('chart_create');        // present tense
amplitudeService.track('Subscription-Upgrade'); // mixed case
```

**✅ Good**:
```typescript
// Consistent snake_case, past tense
amplitudeService.track('user_logged_in');
amplitudeService.track('chart_created');
amplitudeService.track('subscription_upgraded');
```

### 2. Sending Too Much Data

**❌ Bad**:
```typescript
amplitudeService.track('chart_created', {
  chart_data: JSON.stringify(entireChart),  // Too large (> 1000 chars)
  user_bio: user.bio,                        // Unnecessary context
  request_headers: headers,                  // Excessive metadata
});
```

**✅ Good**:
```typescript
amplitudeService.track('chart_created', {
  house_system: 'placidus',      // Relevant property
  has_interpretations: true,      // Boolean flag
  planet_count: 10,              // Useful metric
});
```

### 3. Tracking PII (Personally Identifiable Information)

**❌ Bad**:
```typescript
amplitudeService.track('user_updated_profile', {
  password: newPassword,              // NEVER send passwords
  credit_card: cardNumber,            // NEVER send payment details
  birth_date: '1990-05-15',          // NEVER send exact birth dates
  address: '123 Main St, City',      // NEVER send full addresses
});
```

**✅ Good**:
```typescript
amplitudeService.track('user_updated_profile', {
  fields_changed: ['full_name', 'timezone'],  // What changed, not values
  has_payment_method: true,                   // Boolean flag
  age_range: '25-34',                        // Generalized demographic
  location_city: 'San Francisco',            // City-level only
});
```

### 4. Not Validating Properties

**❌ Bad**:
```typescript
amplitudeService.track('chart_created', {
  house_system: chartData.houseSystem,  // Could be undefined
  name: chartData.personName,           // Could be very long string
  tags: chartData.tags,                 // Could be complex object
});
```

**✅ Good**:
```typescript
amplitudeService.track('chart_created', {
  house_system: chartData.houseSystem || 'placidus',
  has_name: Boolean(chartData.personName),
  tag_count: Array.isArray(chartData.tags) ? chartData.tags.length : 0,
});
```

### 5. Blocking User Actions

**❌ Bad**:
```typescript
const handleSubmit = async () => {
  await amplitudeService.track('form_submitted');  // Blocks user
  await amplitudeService.flush();                  // Blocks user
  await submitForm();
};
```

**✅ Good**:
```typescript
const handleSubmit = async () => {
  amplitudeService.track('form_submitted');  // Fire and forget
  await submitForm();                        // Don't wait for tracking
};
```

### 6. Not Tracking Failures

**❌ Bad**:
```typescript
try {
  const result = await createChart(data);
  amplitudeService.track('chart_created');  // Only tracks success
} catch (error) {
  showError(error);  // Failure not tracked!
}
```

**✅ Good**:
```typescript
try {
  const result = await createChart(data);
  amplitudeService.track('chart_created', {
    house_system: data.house_system,
  });
} catch (error) {
  amplitudeService.track('chart_creation_failed', {
    error_type: error.name,
    error_message: error.message.substring(0, 100),
  });
  showError(error);
}
```

### 7. Forgetting User Context

**❌ Bad**:
```typescript
// Backend - tracking without user_id
amplitude_service.track(
    event_type="chart_created",
    event_properties={"house_system": "placidus"},
    # Missing user_id!
)
```

**✅ Good**:
```typescript
// Backend - always include user_id
amplitude_service.track(
    event_type="chart_created",
    user_id=str(current_user.id),
    event_properties={"house_system": "placidus"},
)
```

---

## Code Examples

### Frontend Examples

#### Example 1: Page View Tracking Hook

**Create reusable hook**: `apps/web/src/hooks/useAmplitudePageView.ts`

```typescript
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { amplitudeService } from '@/services/amplitude';

export function useAmplitudePageView(pageTitle: string, additionalProperties?: Record<string, any>) {
  const location = useLocation();

  useEffect(() => {
    amplitudeService.track('page_viewed', {
      page_path: location.pathname,
      page_title: pageTitle,
      ...additionalProperties,
    });
  }, [location.pathname, pageTitle, additionalProperties]);
}
```

**Usage in component**:
```typescript
import { useAmplitudePageView } from '@/hooks/useAmplitudePageView';

function ChartDetailPage() {
  const { chartId } = useParams();

  useAmplitudePageView('Chart Detail', {
    chart_id: chartId,
  });

  return <div>...</div>;
}
```

#### Example 2: Form Submission Tracking

```typescript
import { useState } from 'react';
import { amplitudeService } from '@/services/amplitude';

function NewChartForm() {
  const [formData, setFormData] = useState({...});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Track form submission (funnel)
    amplitudeService.track('chart_creation_submitted', {
      house_system: formData.houseSystem,
      has_name: Boolean(formData.personName),
    });

    try {
      const result = await createChart(formData);

      // Track success (handled by backend too)
      amplitudeService.track('chart_created', {
        chart_id: result.id,
        house_system: formData.houseSystem,
      });

      navigate(`/charts/${result.id}`);
    } catch (error) {
      // Track failure
      amplitudeService.track('chart_creation_failed', {
        error_type: error instanceof Error ? error.name : 'unknown',
        error_message: error instanceof Error ? error.message.substring(0, 100) : 'Unknown error',
      });

      toast.error('Failed to create chart');
    }
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

#### Example 3: Button Click Tracking with Source Context

**Why `source` matters**: The "Create Chart" button appears in multiple locations (Dashboard, Charts List, Landing Page).
By tracking `source`, we can answer questions like:
- Which entry point converts best?
- Do users from the dashboard create more charts than landing page visitors?
- Should we add the button to more locations?

```typescript
import { amplitudeService } from '@/services/amplitude';
import { Button } from '@/components/ui/button';
import { useLocation } from 'react-router-dom';

function CreateChartButton({ source }: { source: string }) {
  const handleClick = () => {
    amplitudeService.track('chart_creation_started', {
      source: source,  // 'dashboard', 'charts_list', 'landing', 'profile'
    });
    navigate('/charts/new');
  };

  return (
    <Button onClick={handleClick}>
      Create New Chart
    </Button>
  );
}

// Usage in different components
function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <CreateChartButton source="dashboard" />
    </div>
  );
}

function ChartsListPage() {
  return (
    <div>
      <h1>My Charts</h1>
      <CreateChartButton source="charts_list" />
    </div>
  );
}

function LandingPage() {
  return (
    <div>
      <h1>Welcome to Real Astrology</h1>
      <CreateChartButton source="landing" />
    </div>
  );
}
```

**Analysis in Amplitude**:
You can then create a funnel chart showing conversion from `chart_creation_started` → `chart_created`, grouped by `source` property, to see which entry point is most effective.

### Backend Examples

#### Example 4: Endpoint Tracking with Decorator (Future Enhancement)

**Create decorator**: `apps/api/app/core/tracking.py`

```python
from functools import wraps
from app.services.amplitude_service import amplitude_service

def track_amplitude(event_type: str, extract_properties=None):
    """
    Decorator to automatically track Amplitude events on endpoint success.

    Args:
        event_type: Name of the event to track
        extract_properties: Optional function to extract properties from args
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # Extract user_id from current_user dependency
                current_user = kwargs.get('current_user')
                user_id = str(current_user.id) if current_user else None

                # Extract event properties if function provided
                properties = {}
                if extract_properties:
                    properties = extract_properties(result, *args, **kwargs)

                # Track event
                amplitude_service.track(
                    event_type=event_type,
                    user_id=user_id,
                    event_properties=properties,
                )

                return result
            except Exception as e:
                # Track failure
                current_user = kwargs.get('current_user')
                user_id = str(current_user.id) if current_user else None

                amplitude_service.track(
                    event_type=f"{event_type}_failed",
                    user_id=user_id,
                    event_properties={
                        "error_type": type(e).__name__,
                        "error_message": str(e)[:100],
                    },
                )
                raise

        return wrapper
    return decorator
```

**Usage**:
```python
@router.post("/charts", response_model=ChartRead)
@track_amplitude(
    "chart_created",
    extract_properties=lambda result, **kw: {
        "house_system": kw.get('chart_data').house_system,
        "has_name": bool(kw.get('chart_data').person_name),
    }
)
async def create_chart(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await chart_service.create_chart(db, chart_data, current_user.id)
```

#### Example 5: Manual Endpoint Tracking (Current Approach)

```python
from app.services.amplitude_service import amplitude_service

@router.post("/charts", response_model=ChartRead)
async def create_chart(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Create chart
        chart = await chart_service.create_chart(db, chart_data, current_user.id)

        # Track success
        amplitude_service.track(
            event_type="chart_created",
            user_id=str(current_user.id),
            event_properties={
                "house_system": chart_data.house_system,
                "has_name": bool(chart_data.person_name),
                "location_type": "geocoded" if chart_data.lat and chart_data.lon else "manual",
                "timezone": chart_data.birth_timezone,
            },
        )

        return chart

    except ValidationError as e:
        amplitude_service.track(
            event_type="chart_creation_failed",
            user_id=str(current_user.id),
            event_properties={
                "error_type": "validation_error",
                "error_message": str(e)[:100],
            },
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        amplitude_service.track(
            event_type="chart_creation_failed",
            user_id=str(current_user.id),
            event_properties={
                "error_type": type(e).__name__,
                "error_message": str(e)[:100],
            },
        )
        raise
```

#### Example 6: Background Task Tracking

```python
from app.tasks.celery_app import celery_app
from app.services.amplitude_service import amplitude_service

@celery_app.task
def generate_chart_interpretation(chart_id: str, user_id: str):
    """Generate AI interpretation for chart."""
    import time
    start_time = time.time()

    try:
        # Track start
        amplitude_service.track(
            event_type="interpretation_generation_started",
            user_id=user_id,
            event_properties={"chart_id": chart_id},
        )

        # Generate interpretation
        interpretation = ai_service.generate_interpretation(chart_id)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Track success
        amplitude_service.track(
            event_type="interpretation_generated",
            user_id=user_id,
            event_properties={
                "chart_id": chart_id,
                "interpretation_type": interpretation.type,
                "generation_time_ms": duration_ms,
                "used_cache": False,
            },
        )

        # Ensure events are sent before task completes
        amplitude_service.flush()

        return interpretation

    except Exception as e:
        amplitude_service.track(
            event_type="interpretation_generation_failed",
            user_id=user_id,
            event_properties={
                "chart_id": chart_id,
                "error_type": type(e).__name__,
                "error_message": str(e)[:100],
            },
        )
        amplitude_service.flush()
        raise
```

---

## Testing & Debugging

### Disabling Amplitude for Testing

**Backend** (`apps/api/.env`):
```bash
AMPLITUDE_ENABLED=false
```

**Frontend** (`apps/web/.env`):
```bash
VITE_AMPLITUDE_ENABLED=false
```

When disabled, all tracking calls become no-ops (silently ignored).

### Testing Tracking Implementation

**Backend Tests** (`apps/api/tests/test_services/test_amplitude_service.py`):

```python
import pytest
from unittest.mock import MagicMock, patch
from app.services.amplitude_service import AmplitudeService

def test_track_event_when_enabled():
    """Test that events are tracked when enabled."""
    with patch('app.services.amplitude_service.settings') as mock_settings:
        mock_settings.AMPLITUDE_ENABLED = True
        mock_settings.AMPLITUDE_API_KEY = "test_key"

        service = AmplitudeService()
        service.client = MagicMock()

        service.track(
            event_type="test_event",
            user_id="user_123",
            event_properties={"key": "value"},
        )

        service.client.track.assert_called_once()

def test_track_event_when_disabled():
    """Test that events are not tracked when disabled."""
    with patch('app.services.amplitude_service.settings') as mock_settings:
        mock_settings.AMPLITUDE_ENABLED = False

        service = AmplitudeService()

        # Should not raise any errors
        service.track(
            event_type="test_event",
            user_id="user_123",
        )
```

**Frontend Tests** (`apps/web/src/services/__tests__/amplitude.test.ts`):

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as amplitude from '@amplitude/analytics-browser';

vi.mock('@amplitude/analytics-browser');

describe('AmplitudeService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should track events when enabled', async () => {
    process.env.VITE_AMPLITUDE_ENABLED = 'true';
    process.env.VITE_AMPLITUDE_API_KEY = 'test_key';

    const { amplitudeService } = await import('../amplitude');

    amplitudeService.track('test_event', { key: 'value' });

    expect(amplitude.track).toHaveBeenCalledWith('test_event', { key: 'value' });
  });

  it('should not track events when disabled', async () => {
    process.env.VITE_AMPLITUDE_ENABLED = 'false';

    const { amplitudeService } = await import('../amplitude');

    amplitudeService.track('test_event');

    expect(amplitude.track).not.toHaveBeenCalled();
  });
});
```

### Debugging in Development

**Frontend Console Logs**:

The frontend service logs all tracking calls:
```
[Amplitude] Analytics initialized
[Amplitude] Event tracked: user_logged_in
[Amplitude] User identified: 123e4567-e89b-12d3-a456-426614174000
[Amplitude] User identity reset
```

**Backend Logs**:

The backend service uses Loguru for structured logging:
```
2025-01-26 10:30:45.123 | INFO | app.services.amplitude_service:__init__:25 - Amplitude Analytics initialized
2025-01-26 10:31:12.456 | DEBUG | app.services.amplitude_service:track:114 - Amplitude event tracked: user_logged_in
```

### Amplitude Debugger

**Web Debugger**:
1. Install Amplitude Chrome Extension
2. Open browser DevTools → Amplitude tab
3. See real-time events being sent
4. Verify event names and properties

**Alternative - Network Inspector**:
1. Open browser DevTools → Network tab
2. Filter by "amplitude"
3. Inspect HTTP requests to Amplitude API
4. Verify event payloads

---

## Privacy & Compliance

### LGPD/GDPR Considerations

**User Consent**:
- Analytics tracking is covered by our cookie policy
- Users can opt-out via cookie banner
- When implementing opt-out, set `AMPLITUDE_ENABLED=false` for that user

**Data Retention**:
- Amplitude retains data per configured retention policy (default: 5 years)
- User data can be deleted via Amplitude's GDPR API
- Document all tracked properties in Privacy Policy

**User Rights**:
- **Right to Access**: Users can export their data from Amplitude dashboard
- **Right to Deletion**: Implement deletion via Amplitude GDPR API
- **Right to Opt-Out**: Disable tracking when user opts out of analytics

### Data Minimization

Only track data that is:
1. **Necessary** for product decisions
2. **Non-sensitive** (no PII beyond user_id)
3. **Aggregatable** (useful in aggregate analysis)
4. **Documented** (listed in this catalog)

**Example - Good Data Minimization**:
```typescript
// ✅ Good - minimal, relevant data
amplitudeService.track('chart_created', {
  house_system: 'placidus',      // Feature usage
  has_name: true,                // Boolean flag
  timezone: 'America/New_York',  // General location
});

// ❌ Bad - excessive, sensitive data
amplitudeService.track('chart_created', {
  person_name: 'John Doe',            // PII
  birth_datetime: '1990-05-15T10:30', // Sensitive
  exact_location: '40.7128,-74.0060', // Precise location
  full_chart_data: {...},             // Excessive
});
```

### Security Considerations

**API Keys**:
- ✅ Store in environment variables (`.env`)
- ✅ Never commit to version control
- ✅ Use different keys for dev/staging/production
- ❌ Never expose backend API key in frontend code

**Data Transmission**:
- ✅ All data sent over HTTPS
- ✅ Amplitude SDKs use secure connections
- ✅ Events validated before sending

**Access Control**:
- Limit Amplitude dashboard access to team members who need it
- Use role-based access (View-only for analysts, Admin for developers)
- Regularly audit who has access

---

## Checklist for Adding New Events

Before adding a new event, complete this checklist:

- [ ] **Event Name**
  - [ ] Follows `{object}_{action}` pattern
  - [ ] Uses `snake_case`
  - [ ] Uses past tense for completed actions
  - [ ] Is unique and descriptive

- [ ] **Event Properties**
  - [ ] All properties use `snake_case`
  - [ ] All properties have appropriate data types
  - [ ] No PII is sent (passwords, credit cards, etc.)
  - [ ] String properties are < 1000 characters
  - [ ] All properties are documented

- [ ] **Implementation**
  - [ ] Tracked in correct location (frontend vs backend)
  - [ ] Error handling in place (try-catch)
  - [ ] User context included (user_id)
  - [ ] No blocking calls (async/non-blocking)

- [ ] **Testing**
  - [ ] Tested with Amplitude debugger
  - [ ] Verified event appears in Amplitude dashboard
  - [ ] Event properties are correct
  - [ ] Unit tests added (if critical event)

- [ ] **Documentation**
  - [ ] Event added to this catalog
  - [ ] Event documented in code comments
  - [ ] Properties documented
  - [ ] Related issue updated (e.g., #218)

---

## Resources

**Official Documentation**:
- [Amplitude Developer Docs](https://www.docs.developers.amplitude.com/)
- [Amplitude Browser SDK](https://www.docs.developers.amplitude.com/data/sdks/browser-2/)
- [Amplitude Python SDK](https://www.docs.developers.amplitude.com/data/sdks/python/)

**Amplitude Dashboard**:
- [Analytics Dashboard](https://analytics.amplitude.com/)
- [Event Explorer](https://help.amplitude.com/hc/en-us/articles/229313067-Event-Explorer)
- [User Lookup](https://help.amplitude.com/hc/en-us/articles/229313887-User-Lookup)

**Internal Resources**:
- [CLAUDE.md - Amplitude Section](../CLAUDE.md#amplitude-analytics-integration)
- [Issue #83 - Initial Setup](https://github.com/lmeazzini/astro-natal-chart/issues/83)
- [Issue #218 - Comprehensive Tracking Plan](https://github.com/lmeazzini/astro-natal-chart/issues/218)

**Code Locations**:
- Frontend Service: `apps/web/src/services/amplitude.ts`
- Backend Service: `apps/api/app/services/amplitude_service.py`
- Frontend Tests: `apps/web/src/services/__tests__/amplitude.test.ts`
- Backend Tests: `apps/api/tests/test_services/test_amplitude_service.py`

---

## Changelog

**Version 2.1.0** (2026-01-07):
- Added Credit Events section (Issue #305)
- New events: `subscription_renewed`, `credits_low_warning`, `credits_refunded`
- Updated Implementation Status to include credit tracking
- Added detailed event documentation for new events

**Version 2.0.0** (2025-01-26):
- Complete event catalog with ~70 events
- Added Authentication Events section (10 events)
- Added Email Verification Events section (5 events)
- Added Password Reset Events section (6 events)
- Added Chart Events section (13 events)
- Added Profile/Account Events section (8 events)
- Added System Events section (1 event)
- Updated Implementation Status to show all phases complete
- Created companion CSV catalog (`AMPLITUDE_EVENT_CATALOG.csv`)

**Version 1.0.0** (2025-01-26):
- Initial manual created
- Documented event naming conventions
- Documented property guidelines
- Created event catalog with basic events
- Added comprehensive code examples
- Added testing and debugging section
- Added privacy and compliance section

---

## Contributing

To update this manual:

1. Make changes to `docs/AMPLITUDE_BEST_PRACTICES.md`
2. Update the **Changelog** section with date and changes
3. Increment version number (Semantic Versioning)
4. Create PR with changes
5. Tag PR with `documentation` label

**Questions or suggestions?** Open an issue with the `documentation` label.

---

**Last Updated**: 2026-01-07
**Maintainer**: Development Team
**Version**: 2.1.0
