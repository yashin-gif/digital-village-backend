# Village_Project API — Digital Village Backend

গ্রামের মানুষ, পরিবার, রক্তদাতা, যাকাত/সাহায্য, মসজিদ, প্রতিষ্ঠান, স্থান, সংবাদ, ঘোষণা ও জরুরি সেবার জন্য FastAPI ভিত্তিক ব্যাকেন্ড।

## সেটআপ

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # তারপর SECRET_KEY বদলান
python run.py                       # http://127.0.0.1:8000/docs
```

প্রথম অ্যাডমিন তৈরি (একবারই):

```bash
python scripts/create_admin.py --username karim --email karim@example.com --phone 01700000000
```

## .env

| নাম | কাজ |
|---|---|
| `DEBUG` | ডেভেলপমেন্টে `true`। `false` হলে `SECRET_KEY` বদলানো বাধ্যতামূলক |
| `DATABASE_URL` | SQLite (ডিফল্ট) বা PostgreSQL |
| `SECRET_KEY` | টোকেন সই করার কী। `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | ফ্রন্টএন্ডের ঠিকানার JSON লিস্ট |

## ভূমিকা ও অনুমতি

| ভূমিকা | কী করতে পারে |
|---|---|
| সবাই (লগইন ছাড়া) | মসজিদ, প্রতিষ্ঠান, স্থান, সংবাদ, ঘোষণা, জরুরি রিপোর্ট, রক্তদাতার তালিকা দেখা |
| `user` (সদস্য) | লগইন করে গ্রামের মানুষ, পরিবার, শিক্ষা দেখা; জরুরি রিপোর্ট ও সাহায্যের আবেদন পাঠানো; রক্তদাতা যোগ করা |
| `moderator` | উপরের সব + মানুষ, পরিবার, রক্তদাতা, শিক্ষা, প্রতিষ্ঠান, স্থান, সংবাদ, ঘোষণা, মসজিদ, জরুরি সেবার তৈরি/সম্পাদনা/মোছা; যাকাত ও সাহায্যের আবেদন দেখা |
| `admin` | উপরের সব + ইউজার ব্যবস্থাপনা (তৈরি, সম্পাদনা, ভূমিকা, সক্রিয়তা, মোছা) |

সংবেদনশীল তথ্য (জন্ম তারিখ, প্রতিবন্ধী/বিধবা/সাহায্যপ্রার্থী চিহ্ন) শুধু মডারেটর ও অ্যাডমিন দেখে। যাকাতের রেকর্ড শুধু মডারেটর ও অ্যাডমিন দেখে।

প্রতিটি সৃষ্টি, পরিবর্তন ও মোছার কাজ `audit_logs` টেবিলে রেকর্ড হয় (কে, কী, কোথায়)।

## ডেটাবেস আপডেট

নতুন ফিচারের জন্য মাইগ্রেশন চালাতে হবে (একবার):

```bash
alembic upgrade head
```

এটা `help_requests` টেবিলে `user_id` যোগ করে এবং বয়ান/কিতাবের টেবিল বানায়। সার্ভার চালানোর আগে এটা করুন।

## পাসওয়ার্ড রিসেট

`POST /auth/forgot-password` একটা রিসেট টোকেন তৈরি করে `send_notification` দিয়ে পাঠায়।
এখনো কোনো ইমেইল/SMS প্রোভাইডার যুক্ত নেই: ডেভেলপমেন্টে (`DEBUG=true`) টোকেন সার্ভারের লগে দেখা যায়। প্রোডাকশনে `app/services/notification_service.py` এ SMTP বা SMS যুক্ত করতে হবে। টোকেন কখনো API উত্তরে ফেরত যায় না।

## API ওভারভিউ

| রিসোর্স | পাথ | লেখা/পড়ার নিয়ম |
|---|---|---|
| Auth | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/me`, `/auth/forgot-password`, `/auth/reset-password` | — |
| ইউজার (অ্যাডমিন) | `/admin/users` (GET, POST), `/admin/users/{id}` (PATCH, DELETE), `/admin/users/{id}/role?role=`, `/admin/users/{id}/status?is_active=` | admin |
| মানুষ | `/people/` | পড়া: login · লেখা: staff |
| পরিবার | `/families/` | পড়া: login · লেখা: staff |
| রক্তদাতা | `/blood/` | পড়া: সবাই · যোগ: login · বদলানো/মোছা: staff |
| শিক্ষা | `/education/` | পড়া: login · লেখা: staff |
| যাকাত | `/zakat/` | পড়া ও লেখা: staff |
| সাহায্যের আবেদন | `/help-requests/` | পড়া: staff · যোগ: login · বদলানো/মোছা: staff |
| মসজিদ | `/mosques/` | পড়া: সবাই · লেখা: staff |
| প্রতিষ্ঠান | `/institutions/` | পড়া: সবাই · লেখা: staff |
| স্থান | `/places/` | পড়া: সবাই · লেখা: staff |
| সংবাদ | `/news/` | পড়া: সবাই (অপ্রকাশিত শুধু staff) · লেখা: staff |
| ঘোষণা | `/announcements/` | পড়া: সবাই (নিষ্ক্রিয় শুধু staff) · লেখা: staff |
| জরুরি সেবা | `/emergency/` | পড়া: সবাই · যোগ: login · বদলানো/মোছা: staff |
| বয়ান | `/bayan/` | পড়া: সবাই (অপ্রকাশিত শুধু staff) · লেখা: staff |
| কিতাব | `/kitab/` | পড়া: সবাই · লেখা: staff |
| কিতাব পাঠ | `/kitab-progress/` | পড়া: সবাই · লেখা: staff |
| আমার আবেদন | `/my/help-requests` | লগইন করা সদস্য, নিজের আবেদন |

প্রতিটি সাধারণ CRUD রিসোর্সে `GET /` তালিকা (পাতা, খোঁজ, ফিল্টার) এর জন্য নিচের "বড় ডেটা" অংশ দেখুন।

প্রতিটি রিসোর্সে `GET /`, `GET /{id}`, `POST /`, `PATCH /{id}`, `DELETE /{id}` আছে।

## কোড কাঠামো

- `app/core/crud.py` — সব সাধারণ রিসোর্সের CRUD রাউটার এখান থেকে তৈরি হয়। অনুমতি, ফিল্টার, ভ্যালিডেশন ও অডিট এক জায়গায়।
- `app/routers/*.py` — প্রতিটি মডিউলের নিয়ম (কে পড়বে, কী যাচাই হবে)।
- `app/dependencies.py` — `get_current_user`, `get_optional_user`, `require_staff`, `require_admin_user`।
- `app/schemas/common.py` — আপডেটের জন্য ঐচ্ছিক ফিল্ডের স্কিমা।
- `app/services/audit_service.py` — অডিট লগ।


## বড় ডেটা (লক্ষাধিক রেকর্ড)

### তালিকা API

প্রতিটি তালিকা এন্ডপয়েন্ট (`GET /people/`, `/families/`, `/blood/`, `/bayan/` ইত্যাদি):

| প্যারামিটার | কাজ |
|---|---|
| `limit` | একবারে কতটি (সর্বোচ্চ ২০০)। না দিলে রিসোর্সের ডিফল্ট |
| `offset` | কতটি বাদ দিয়ে শুরু (পাতা = `offset = (পাতা-১) * limit`) |
| `q` | খোঁজ। যেমন মানুষে নাম, ফোন, পেশা, এলাকা — অংশ মিললেই হবে |
| `order` | `asc` (ডিফল্ট) বা `desc` |
| ফিল্টার | রিসোর্স অনুযায়ী, যেমন `people?blood_group=A+`, `bayan?mosque_id=3&session_date_from=2026-10-11` |

উত্তরে `X-Total-Count` হেডারে মোট সংখ্যা থাকে — ফ্রন্টএন্ড এটা দিয়েই পাতার সংখ্যা ঠিক করে।

ডিফল্ট সীমা: মানুষ, পরিবার, রক্তদাতা, শিক্ষা, যাকাত, সাহায্য = ৫০; বয়ান = ১০০; জরুরি সেবা = ১০০; কিতাব-পাঠ = ১০০। সংবাদ, ঘোষণা, মসজিদ, প্রতিষ্ঠান, স্থান ধীরে বাড়ে, তাই সেগুলো পুরোটাই যায়।

### কেন দ্রুত থাকে

- **পাতা ভিত্তিক:** সার্ভার কখনো পুরো টেবিল পাঠায় না।
- **ইনডেক্স:** ফিল্টার ও সাজানোর কলামে (যেমন `people.blood_group`, `bayan.session_date`) ইনডেক্স আছে।
- **ট্রাইগ্রাম (PostgreSQL):** `q` খোঁজ `%অংশ%` দিয়ে হলেও লাখো সারিতে দ্রুত চলে।
- **এক কুয়েরিতে নাম:** পরিবারের প্রধানের নাম, দাতার নাম, মসজিদের নাম ইত্যাদি একবারে সব সারির জন্য আনা হয় (`app/core/enrich.py`), প্রতি সারির জন্য আলাদা কুয়েরি নয়।
- **কানেকশন পুল:** PostgreSQL-এ একসাথে অনেক ব্যবহারকারীর জন্য (`database.py`)।

### PostgreSQL-এ যাওয়া (বড় ডেটার জন্য সুপারিশকৃত)

SQLite একজনের জন্য ভালো, কিন্তু অনেক ব্যবহারকারী ও লাখো রেকর্ডে PostgreSQL দরকার।

1. PostgreSQL 14+ ইনস্টল করুন এবং একটা ডেটাবেস বানান:
   ```sql
   CREATE DATABASE digital_village;
   ```
2. `.env` এ লিখুন:
   ```
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/digital_village
   DEBUG=false
   SECRET_KEY=<নতুন দীর্ঘ কী>
   ```
3. **নতুন ডেটাবেস:** আগে টেবিল বানান, তারপর ইনডেক্স:
   ```bash
   python run.py          # একবার চালিয়ে বন্ধ করুন (টেবিল তৈরি হবে)
   alembic stamp head
   python scripts/setup_indexes.py
   ```
4. **SQLite থেকে ডেটা সরাতে:** সরাসরি কপি করার টুল (যেমন `pgloader`) ব্যবহার করুন, তারপর `alembic stamp head` ও `python scripts/setup_indexes.py`।

`scripts/setup_indexes.py` বারবার চালালেও নিরাপদ: যা আছে তা আবার বানায় না।

### প্রোডাকশনে চালানো

```bash
pip install gunicorn
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000
```
`-w` (ওয়ার্কার সংখ্যা) সাধারণত CPU কোরের সমান বা দ্বিগুণ। সামনে Nginx রেখে স্ট্যাটিক ফাইল ও HTTPS দিন।
