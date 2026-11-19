create extension if not exists postgis;

create table creators (
  id bigserial primary key, platform text not null, handle text not null,
  followers int, consent_face_analysis boolean default false,
  unique (platform, handle)
);
create table venues (
  id bigserial primary key, name text not null, category text not null
    check (category in ('restaurante','bar','doceria','cafe','padaria','outro')),
  address text, city text, geom geography(point, 4326),
  verified boolean default false  -- passou pela curadoria
);
create table dishes (
  id bigserial primary key, venue_id bigint references venues on delete cascade,
  name text not null, kind text, price_cents int, unique (venue_id, name)
);
create table posts (
  id bigserial primary key, creator_id bigint references creators,
  url text unique not null, posted_at timestamptz, transcript text,
  extraction jsonb,            -- saída bruta do LLM
  status text default 'pending' -- pending | extracted | curated | rejected
);
create table post_mentions (
  post_id bigint references posts on delete cascade,
  venue_id bigint references venues, dish_id bigint references dishes,
  confidence real, primary key (post_id, venue_id, dish_id)
);
create table comments (
  id bigserial primary key, post_id bigint references posts on delete cascade,
  author_hash text, body text, sentiment text check (sentiment in ('pos','neu','neg','spam')),
  venue_id bigint references venues, dish_id bigint references dishes
);
create table emotion_signals (
  post_id bigint references posts on delete cascade, dish_id bigint references dishes,
  t_start real, t_end real, face_valence real, voice_arousal real,
  predicted_neural_engagement real,  -- TRIBE (a validar)
  primary key (post_id, dish_id, t_start)
);
create table scores (
  dish_id bigint references dishes, venue_id bigint references venues,
  pos int, total int, wilson_lb real, computed_at timestamptz default now()
);
create index on venues using gist (geom);
