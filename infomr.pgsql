--
-- PostgreSQL database dump
--

-- Dumped from database version 11.5
-- Dumped by pg_dump version 11.5

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
-- Name: vec3f; Type: TYPE; Schema: public; Owner: Tiziano
--

CREATE TYPE public.vec3f AS (
	x double precision,
	y double precision,
	z double precision
);


ALTER TYPE public.vec3f OWNER TO "Tiziano";

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: eigenvectors; Type: TABLE; Schema: public; Owner: Tiziano
--

CREATE TABLE public.eigenvectors (
    eigen_id integer NOT NULL,
    eigen_value double precision
);


ALTER TABLE public.eigenvectors OWNER TO "Tiziano";

--
-- Name: eigenvectors_eigen_id_seq; Type: SEQUENCE; Schema: public; Owner: Tiziano
--

CREATE SEQUENCE public.eigenvectors_eigen_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.eigenvectors_eigen_id_seq OWNER TO "Tiziano";

--
-- Name: eigenvectors_eigen_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Tiziano
--

ALTER SEQUENCE public.eigenvectors_eigen_id_seq OWNED BY public.eigenvectors.eigen_id;


--
-- Name: meshes; Type: TABLE; Schema: public; Owner: Tiziano
--

CREATE TABLE public.meshes (
    mesh_id integer NOT NULL,
    filepath character varying(50)
);


ALTER TABLE public.meshes OWNER TO "Tiziano";

--
-- Name: mesh_mesh_id_seq; Type: SEQUENCE; Schema: public; Owner: Tiziano
--

CREATE SEQUENCE public.mesh_mesh_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mesh_mesh_id_seq OWNER TO "Tiziano";

--
-- Name: mesh_mesh_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Tiziano
--

ALTER SEQUENCE public.mesh_mesh_id_seq OWNED BY public.meshes.mesh_id;


--
-- Name: meshtypes; Type: TABLE; Schema: public; Owner: Tiziano
--

CREATE TABLE public.meshtypes (
    meshtype_id integer NOT NULL,
    type character varying(50),
    mesh_id integer,
    averagepolygons double precision NOT NULL,
    averagevertices double precision NOT NULL
);


ALTER TABLE public.meshtypes OWNER TO "Tiziano";

--
-- Name: meshtypes_meshtype_id_seq; Type: SEQUENCE; Schema: public; Owner: Tiziano
--

CREATE SEQUENCE public.meshtypes_meshtype_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.meshtypes_meshtype_id_seq OWNER TO "Tiziano";

--
-- Name: meshtypes_meshtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Tiziano
--

ALTER SEQUENCE public.meshtypes_meshtype_id_seq OWNED BY public.meshtypes.meshtype_id;


--
-- Name: triangular_poly; Type: TABLE; Schema: public; Owner: Tiziano
--

CREATE TABLE public.triangular_poly (
    vertex1_id integer NOT NULL,
    vertex2_id integer NOT NULL,
    vertex3_id integer NOT NULL
);


ALTER TABLE public.triangular_poly OWNER TO "Tiziano";

--
-- Name: vertices; Type: TABLE; Schema: public; Owner: Tiziano
--

CREATE TABLE public.vertices (
    vertex_id integer NOT NULL,
    pos public.vec3f NOT NULL,
    mesh_id integer
);


ALTER TABLE public.vertices OWNER TO "Tiziano";

--
-- Name: vertices_vertex_id_seq; Type: SEQUENCE; Schema: public; Owner: Tiziano
--

CREATE SEQUENCE public.vertices_vertex_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vertices_vertex_id_seq OWNER TO "Tiziano";

--
-- Name: vertices_vertex_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: Tiziano
--

ALTER SEQUENCE public.vertices_vertex_id_seq OWNED BY public.vertices.vertex_id;


--
-- Name: eigenvectors eigen_id; Type: DEFAULT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.eigenvectors ALTER COLUMN eigen_id SET DEFAULT nextval('public.eigenvectors_eigen_id_seq'::regclass);


--
-- Name: meshes mesh_id; Type: DEFAULT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.meshes ALTER COLUMN mesh_id SET DEFAULT nextval('public.mesh_mesh_id_seq'::regclass);


--
-- Name: meshtypes meshtype_id; Type: DEFAULT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.meshtypes ALTER COLUMN meshtype_id SET DEFAULT nextval('public.meshtypes_meshtype_id_seq'::regclass);


--
-- Name: vertices vertex_id; Type: DEFAULT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.vertices ALTER COLUMN vertex_id SET DEFAULT nextval('public.vertices_vertex_id_seq'::regclass);


--
-- Data for Name: eigenvectors; Type: TABLE DATA; Schema: public; Owner: Tiziano
--

COPY public.eigenvectors (eigen_id, eigen_value) FROM stdin;
\.


--
-- Data for Name: meshes; Type: TABLE DATA; Schema: public; Owner: Tiziano
--

COPY public.meshes (mesh_id, filepath) FROM stdin;
\.


--
-- Data for Name: meshtypes; Type: TABLE DATA; Schema: public; Owner: Tiziano
--

COPY public.meshtypes (meshtype_id, type, mesh_id, averagepolygons, averagevertices) FROM stdin;
\.


--
-- Data for Name: triangular_poly; Type: TABLE DATA; Schema: public; Owner: Tiziano
--

COPY public.triangular_poly (vertex1_id, vertex2_id, vertex3_id) FROM stdin;
\.


--
-- Data for Name: vertices; Type: TABLE DATA; Schema: public; Owner: Tiziano
--

COPY public.vertices (vertex_id, pos, mesh_id) FROM stdin;
\.


--
-- Name: eigenvectors_eigen_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Tiziano
--

SELECT pg_catalog.setval('public.eigenvectors_eigen_id_seq', 1, false);


--
-- Name: mesh_mesh_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Tiziano
--

SELECT pg_catalog.setval('public.mesh_mesh_id_seq', 1, false);


--
-- Name: meshtypes_meshtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Tiziano
--

SELECT pg_catalog.setval('public.meshtypes_meshtype_id_seq', 1, false);


--
-- Name: vertices_vertex_id_seq; Type: SEQUENCE SET; Schema: public; Owner: Tiziano
--

SELECT pg_catalog.setval('public.vertices_vertex_id_seq', 1, false);


--
-- Name: eigenvectors eigenvectors_pkey; Type: CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.eigenvectors
    ADD CONSTRAINT eigenvectors_pkey PRIMARY KEY (eigen_id);


--
-- Name: meshes mesh_pkey; Type: CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.meshes
    ADD CONSTRAINT mesh_pkey PRIMARY KEY (mesh_id);


--
-- Name: meshtypes meshtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.meshtypes
    ADD CONSTRAINT meshtypes_pkey PRIMARY KEY (meshtype_id);


--
-- Name: triangular_poly polygons_pkey; Type: CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.triangular_poly
    ADD CONSTRAINT polygons_pkey PRIMARY KEY (vertex1_id, vertex2_id, vertex3_id);


--
-- Name: vertices vertices_pkey; Type: CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.vertices
    ADD CONSTRAINT vertices_pkey PRIMARY KEY (vertex_id);


--
-- Name: meshtypes meshtypes_mesh_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.meshtypes
    ADD CONSTRAINT meshtypes_mesh_id_fkey FOREIGN KEY (mesh_id) REFERENCES public.meshes(mesh_id);


--
-- Name: triangular_poly polygons_vertex1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.triangular_poly
    ADD CONSTRAINT polygons_vertex1_id_fkey FOREIGN KEY (vertex1_id) REFERENCES public.vertices(vertex_id);


--
-- Name: triangular_poly polygons_vertex2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.triangular_poly
    ADD CONSTRAINT polygons_vertex2_id_fkey FOREIGN KEY (vertex2_id) REFERENCES public.vertices(vertex_id);


--
-- Name: triangular_poly polygons_vertex3_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.triangular_poly
    ADD CONSTRAINT polygons_vertex3_id_fkey FOREIGN KEY (vertex3_id) REFERENCES public.vertices(vertex_id);


--
-- Name: vertices vertices_mesh_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Tiziano
--

ALTER TABLE ONLY public.vertices
    ADD CONSTRAINT vertices_mesh_id_fkey FOREIGN KEY (mesh_id) REFERENCES public.meshes(mesh_id);


--
-- PostgreSQL database dump complete
--

