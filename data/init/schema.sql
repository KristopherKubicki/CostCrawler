--
-- PostgreSQL database dump
--

-- Dumped from database version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: waymed
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO waymed;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: waymed
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO waymed;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: waymed
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO waymed;

--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: waymed
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: agg_procedure; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.agg_procedure (
    agg_procedure_id integer NOT NULL,
    name character varying(50) NOT NULL,
    live boolean DEFAULT false NOT NULL,
    true_procedure_count integer DEFAULT 0,
    creation_time timestamp without time zone DEFAULT now() NOT NULL,
    live_time timestamp without time zone
);


ALTER TABLE public.agg_procedure OWNER TO waymed;

--
-- Name: agg_procedure_agg_procedure_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.agg_procedure_agg_procedure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.agg_procedure_agg_procedure_id_seq OWNER TO waymed;

--
-- Name: agg_procedure_agg_procedure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.agg_procedure_agg_procedure_id_seq OWNED BY public.agg_procedure.agg_procedure_id;


--
-- Name: facility; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.facility (
    facility_id integer NOT NULL,
    name character varying(50) NOT NULL,
    display_name character varying(50) NOT NULL,
    location_name character varying(50),
    location public.geometry(Point,4326) NOT NULL,
    creation_time timestamp without time zone DEFAULT now() NOT NULL,
    edit_time timestamp without time zone DEFAULT now() NOT NULL,
    scrape_time timestamp without time zone,
    version integer DEFAULT 1 NOT NULL
);


ALTER TABLE public.facility OWNER TO waymed;

--
-- Name: raw_charge; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.raw_charge (
    raw_charge_id integer NOT NULL,
    facility_id integer NOT NULL,
    raw_procedure_id integer NOT NULL,
    charge_type character varying(3) DEFAULT 'CM'::character varying NOT NULL,
    charge numeric(10,2) NOT NULL,
    alt_charge numeric(10,2),
    live boolean DEFAULT true NOT NULL,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    creation_time timestamp without time zone DEFAULT now(),
    live_time timestamp without time zone DEFAULT now(),
    scrape_time timestamp without time zone DEFAULT now()
);


ALTER TABLE public.raw_charge OWNER TO waymed;

--
-- Name: raw_charge_raw_charge_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.raw_charge_raw_charge_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.raw_charge_raw_charge_id_seq OWNER TO waymed;

--
-- Name: raw_charge_raw_charge_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.raw_charge_raw_charge_id_seq OWNED BY public.raw_charge.raw_charge_id;


--
-- Name: raw_procedure; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.raw_procedure (
    raw_procedure_id integer NOT NULL,
    true_procedure_id integer,
    bill_id character varying(32),
    description character varying(128),
    live boolean DEFAULT true NOT NULL,
    raw_charge_count integer DEFAULT 0 NOT NULL,
    creation_time timestamp without time zone DEFAULT now(),
    live_time timestamp without time zone DEFAULT now(),
    map_time timestamp without time zone
);


ALTER TABLE public.raw_procedure OWNER TO waymed;

--
-- Name: raw_procedure_raw_procedure_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.raw_procedure_raw_procedure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.raw_procedure_raw_procedure_id_seq OWNER TO waymed;

--
-- Name: raw_procedure_raw_procedure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.raw_procedure_raw_procedure_id_seq OWNED BY public.raw_procedure.raw_procedure_id;


--
-- Name: true_procedure; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.true_procedure (
    true_procedure_id integer NOT NULL,
    agg_procedure_id integer,
    hcpc_code character(12) NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    raw_procedure_count integer DEFAULT 0 NOT NULL,
    creation_time timestamp without time zone DEFAULT now(),
    map_time timestamp without time zone
);


ALTER TABLE public.true_procedure OWNER TO waymed;

--
-- Name: true_procedure_true_procedure_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.true_procedure_true_procedure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.true_procedure_true_procedure_id_seq OWNER TO waymed;

--
-- Name: true_procedure_true_procedure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.true_procedure_true_procedure_id_seq OWNED BY public.true_procedure.true_procedure_id;


--
-- Name: zone; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.zone (
    zone_id integer NOT NULL,
    name character varying(50) NOT NULL,
    state character(2) NOT NULL,
    location public.geometry(Point,4326) NOT NULL,
    type character(3) DEFAULT 'CIT'::bpchar NOT NULL,
    status character(3) DEFAULT 'DIS'::bpchar NOT NULL,
    view_count integer DEFAULT 0 NOT NULL,
    creation_time timestamp without time zone DEFAULT now() NOT NULL,
    status_time timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.zone OWNER TO waymed;

--
-- Name: zone_procedure; Type: TABLE; Schema: public; Owner: waymed
--

CREATE TABLE public.zone_procedure (
    zone_procedure_id integer NOT NULL,
    agg_procedure_id integer NOT NULL,
    zone_id integer,
    live boolean DEFAULT false NOT NULL,
    avg_charge money,
    agg_procedure_count integer DEFAULT 0 NOT NULL,
    view_count integer DEFAULT 0,
    creation_time timestamp without time zone DEFAULT now() NOT NULL,
    live_time timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.zone_procedure OWNER TO waymed;

--
-- Name: zone_procedure_zone_procedure_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.zone_procedure_zone_procedure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zone_procedure_zone_procedure_id_seq OWNER TO waymed;

--
-- Name: zone_procedure_zone_procedure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.zone_procedure_zone_procedure_id_seq OWNED BY public.zone_procedure.zone_procedure_id;


--
-- Name: zone_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: waymed
--

CREATE SEQUENCE public.zone_zone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zone_zone_id_seq OWNER TO waymed;

--
-- Name: zone_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: waymed
--

ALTER SEQUENCE public.zone_zone_id_seq OWNED BY public.zone.zone_id;


--
-- Name: agg_procedure agg_procedure_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.agg_procedure ALTER COLUMN agg_procedure_id SET DEFAULT nextval('public.agg_procedure_agg_procedure_id_seq'::regclass);


--
-- Name: raw_charge raw_charge_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_charge ALTER COLUMN raw_charge_id SET DEFAULT nextval('public.raw_charge_raw_charge_id_seq'::regclass);


--
-- Name: raw_procedure raw_procedure_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_procedure ALTER COLUMN raw_procedure_id SET DEFAULT nextval('public.raw_procedure_raw_procedure_id_seq'::regclass);


--
-- Name: true_procedure true_procedure_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.true_procedure ALTER COLUMN true_procedure_id SET DEFAULT nextval('public.true_procedure_true_procedure_id_seq'::regclass);


--
-- Name: zone zone_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone ALTER COLUMN zone_id SET DEFAULT nextval('public.zone_zone_id_seq'::regclass);


--
-- Name: zone_procedure zone_procedure_id; Type: DEFAULT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone_procedure ALTER COLUMN zone_procedure_id SET DEFAULT nextval('public.zone_procedure_zone_procedure_id_seq'::regclass);


--
-- Name: agg_procedure agg_procedure_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.agg_procedure
    ADD CONSTRAINT agg_procedure_pkey PRIMARY KEY (agg_procedure_id);


--
-- Name: raw_procedure bill_description; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_procedure
    ADD CONSTRAINT bill_description UNIQUE (bill_id, description);


--
-- Name: facility facility_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.facility
    ADD CONSTRAINT facility_pkey PRIMARY KEY (facility_id);


--
-- Name: raw_charge facility_proc_charge; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_charge
    ADD CONSTRAINT facility_proc_charge UNIQUE (facility_id, raw_procedure_id, charge_type, start_time);


--
-- Name: zone name_state; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone
    ADD CONSTRAINT name_state UNIQUE (name, state, type);


--
-- Name: raw_charge raw_charge_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_charge
    ADD CONSTRAINT raw_charge_pkey PRIMARY KEY (raw_charge_id);


--
-- Name: raw_procedure raw_procedure_bill_id_description_key; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_procedure
    ADD CONSTRAINT raw_procedure_bill_id_description_key UNIQUE (bill_id, description);


--
-- Name: raw_procedure raw_procedure_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_procedure
    ADD CONSTRAINT raw_procedure_pkey PRIMARY KEY (raw_procedure_id);


--
-- Name: true_procedure true_procedure_hcpc_code_key; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.true_procedure
    ADD CONSTRAINT true_procedure_hcpc_code_key UNIQUE (hcpc_code);


--
-- Name: true_procedure true_procedure_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.true_procedure
    ADD CONSTRAINT true_procedure_pkey PRIMARY KEY (true_procedure_id);


--
-- Name: zone zone_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone
    ADD CONSTRAINT zone_pkey PRIMARY KEY (zone_id);


--
-- Name: zone_procedure zone_procedure_pkey; Type: CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone_procedure
    ADD CONSTRAINT zone_procedure_pkey PRIMARY KEY (zone_procedure_id);


--
-- Name: facility_proc_charge_null; Type: INDEX; Schema: public; Owner: waymed
--

CREATE UNIQUE INDEX facility_proc_charge_null ON public.raw_charge USING btree (facility_id, raw_procedure_id, charge_type) WHERE (start_time IS NULL);


--
-- Name: raw_charge raw_charge_facility_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_charge
    ADD CONSTRAINT raw_charge_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES public.facility(facility_id);


--
-- Name: raw_charge raw_charge_raw_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_charge
    ADD CONSTRAINT raw_charge_raw_procedure_id_fkey FOREIGN KEY (raw_procedure_id) REFERENCES public.raw_procedure(raw_procedure_id);


--
-- Name: raw_procedure raw_procedure_true_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.raw_procedure
    ADD CONSTRAINT raw_procedure_true_procedure_id_fkey FOREIGN KEY (true_procedure_id) REFERENCES public.true_procedure(true_procedure_id);


--
-- Name: true_procedure true_procedure_agg_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.true_procedure
    ADD CONSTRAINT true_procedure_agg_procedure_id_fkey FOREIGN KEY (agg_procedure_id) REFERENCES public.agg_procedure(agg_procedure_id);


--
-- Name: zone_procedure zone_procedure_agg_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone_procedure
    ADD CONSTRAINT zone_procedure_agg_procedure_id_fkey FOREIGN KEY (agg_procedure_id) REFERENCES public.agg_procedure(agg_procedure_id);


--
-- Name: zone_procedure zone_procedure_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: waymed
--

ALTER TABLE ONLY public.zone_procedure
    ADD CONSTRAINT zone_procedure_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zone(zone_id);


--
-- PostgreSQL database dump complete
--

