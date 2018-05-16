drop table vessel_location;

CREATE TABLE vessel_location (
  id serial PRIMARY KEY,
  timestamp timestamp,
  mmsi int,
  location geography(POINT),
  sog numeric(4, 1),
  cog numeric(4, 1),
  navstat int,
  posacc bit,
  raim bit,
  heading int,
  timestamp_seconds int
);

drop table vessel_metadata;

create table vessel_metadata (
  id serial PRIMARY KEY,
  timestamp timestamp,
  name varchar,
  callsign varchar,
  imo int,
  mmsi int,
  destination varchar,
  eta int,
  draught int,
  pos_type int,
  reference_point_a int,
  reference_point_b int,
  reference_point_c int,
  reference_point_d int,
  ship_type int
)
