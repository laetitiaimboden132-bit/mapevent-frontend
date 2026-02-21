-- Événements Valais pour MapEventAI
-- Généré le 2026-02-06 15:34:23
-- 300 événements

-- Ajouter la colonne source_url si elle n'existe pas
ALTER TABLE events ADD COLUMN IF NOT EXISTS source_url TEXT;

-- Créer un utilisateur système pour le scraper s'il n'existe pas
INSERT INTO users (id, email, username) VALUES ('system_scraper', 'scraper@mapevent.world', 'MapEvent Scraper') ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Édition 2026',
    'La commune de Fully vous invite à marché gourmand. Rendez-vous au/à la Marché de Fully pour un moment exceptionnel.',
    'Place Centrale 18, Fully, Valais, Suisse',
    46.1341717402533,
    7.117167345563077,
    '2026-03-01',
    '09:00:00',
    '2026-03-01',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.fully.ch/agenda/event-1388',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto au Salle Polyvalente de Saint-Maurice',
    'Loto organisé(e) au/à la Salle Polyvalente de Saint-Maurice, Saint-Maurice. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 44, Saint-Maurice, Valais, Suisse',
    46.21432690297488,
    6.996062610462074,
    '2026-03-01',
    '19:30:00',
    '2026-03-01',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.saintmaurice.ch/agenda/event-1207',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique',
    'Festival de musique organisé(e) au/à la Caves Orsat, Martigny. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 12, Martigny, Valais, Suisse',
    46.09501538177836,
    7.069342471530686,
    '2026-03-02',
    '19:00:00',
    '2026-03-04',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.martigny.ch/agenda/event-6020',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Édition 2026',
    'Rendez-vous à Visp pour concert de musique classique. Cet événement se tiendra au/à la Théâtre La Poste. Ne manquez pas cette occasion unique!',
    'Route Cantonale 14, Visp, Valais, Suisse',
    46.29810165424781,
    7.886183826708958,
    '2026-03-03',
    '22:00:00',
    '2026-03-03',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.visp.ch/agenda/event-6341',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Édition 2026',
    'Spectacle de théâtre organisé(e) au/à la Centre de Congrès le Régent, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 47, Crans-Montana, Valais, Suisse',
    46.31164005311618,
    7.47938897667558,
    '2026-03-04',
    '14:30:00',
    '2026-03-04',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-3648',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ',
    'Soirée DJ organisé(e) au/à la Château de Villa, Sierre. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 45, Sierre, Valais, Suisse',
    46.2879538039283,
    7.534926335826481,
    '2026-03-05',
    '19:30:00',
    '2026-03-05',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.sierre.ch/agenda/event-4492',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Centre de Congrès le Régent',
    'Découvrez fête de village au/à la Centre de Congrès le Régent de Crans-Montana. Un moment convivial à partager en famille ou entre amis.',
    'Rue de l''Église 28, Crans-Montana, Valais, Suisse',
    46.302913638872575,
    7.480883075496606,
    '2026-03-07',
    '19:00:00',
    '2026-03-07',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-8381',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Salle Communale',
    'Découvrez fête de village au/à la Salle Communale de Visp. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 15, Visp, Valais, Suisse',
    46.29754721416461,
    7.879009477583291,
    '2026-03-07',
    '15:00:00',
    '2026-03-07',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.visp.ch/agenda/event-1657',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ',
    'Rendez-vous à Brig pour soirée dj. Cet événement se tiendra au/à la Stockalperschloss. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 2, Brig, Valais, Suisse',
    46.31252422417756,
    7.986868192308889,
    '2026-03-08',
    '22:30:00',
    '2026-03-08',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.brig.ch/agenda/event-9707',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante - Monthey',
    'La commune de Monthey vous invite à brocante. Rendez-vous au/à la Salle Communale pour un moment exceptionnel.',
    'Rue du Rhône 24, Monthey, Valais, Suisse',
    46.2548671043016,
    6.952320386252189,
    '2026-03-10',
    '09:00:00',
    '2026-03-10',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.monthey.ch/agenda/event-4938',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert - Édition 2026',
    'Concert organisé(e) au/à la Église de Zermatt, Zermatt. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 44, Zermatt, Valais, Suisse',
    46.019138685659534,
    7.751220047920007,
    '2026-03-10',
    '19:00:00',
    '2026-03-10',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-9160',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante - Crans-Montana',
    'Découvrez brocante au/à la Casino Crans-Montana de Crans-Montana. Un moment convivial à partager en famille ou entre amis.',
    'Rue de l''Église 23, Crans-Montana, Valais, Suisse',
    46.30571461064092,
    7.4804246015685125,
    '2026-03-11',
    '08:30:00',
    '2026-03-11',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-7942',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage - Zermatt',
    'Zermatt accueille vernissage le 11 March 2026. Venez nombreux au/à la Vernissage Hotel!',
    'Chemin des Vignes 44, Zermatt, Valais, Suisse',
    46.018226118824025,
    7.7447277937797585,
    '2026-03-11',
    '20:00:00',
    '2026-03-11',
    '["Culture > Expositions"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-3202',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage à Salvan',
    'Salvan accueille vernissage le 11 March 2026. Venez nombreux au/à la Galerie de Salvan!',
    'Avenue de la Gare 16, Salvan, Valais, Suisse',
    46.121177245488425,
    7.016551106626743,
    '2026-03-11',
    '19:00:00',
    '2026-03-11',
    '["Culture > Expositions"]'::jsonb,
    'https://www.salvan.ch/agenda/event-9236',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence',
    'Découvrez conférence au/à la Château de Tourbillon de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 24, Sion, Valais, Suisse',
    46.23413028415091,
    7.364712848675402,
    '2026-03-13',
    '10:30:00',
    '2026-03-13',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.sion.ch/agenda/event-2684',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique au Salle polyvalente',
    'Découvrez festival de musique au/à la Salle polyvalente de Nendaz. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 38, Nendaz, Valais, Suisse',
    46.18788158428529,
    7.29505912778336,
    '2026-03-14',
    '19:30:00',
    '2026-03-16',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-1643',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel - Sierre',
    'Rendez-vous à Sierre pour salon professionnel. Cet événement se tiendra au/à la Château de Villa. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 21, Sierre, Valais, Suisse',
    46.29557979681875,
    7.539636229429072,
    '2026-03-14',
    '18:00:00',
    '2026-03-14',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.sierre.ch/agenda/event-2262',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale - Printemps 2026',
    'Découvrez comédie musicale au/à la Théâtre de Saxon de Saxon. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 2, Saxon, Valais, Suisse',
    46.145732814310016,
    7.163126628171603,
    '2026-03-18',
    '10:30:00',
    '2026-03-18',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.saxon.ch/agenda/event-4221',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Édition 2026',
    'Découvrez exposition d''art au/à la Église de Verbier de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 6, Verbier, Valais, Suisse',
    46.09899734939577,
    7.230252293784272,
    '2026-03-20',
    '18:30:00',
    '2026-03-20',
    '["Culture > Expositions"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5742',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval - Édition 2026',
    'La commune de Ayent vous invite à carnaval. Rendez-vous au/à la Place de Ayent pour un moment exceptionnel.',
    'Route Cantonale 12, Ayent, Valais, Suisse',
    46.28225472661388,
    7.418789993012378,
    '2026-03-20',
    '19:00:00',
    '2026-03-20',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.ayent.ch/agenda/event-6550',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Édition 2026',
    'Rendez-vous à Ovronnaz pour concert de musique classique. Cet événement se tiendra au/à la Salle de Ovronnaz. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 9, Ovronnaz, Valais, Suisse',
    46.187894461588186,
    7.1657644736232555,
    '2026-03-20',
    '22:00:00',
    '2026-03-20',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-9714',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Martigny',
    'Découvrez marché de printemps au/à la Fondation Gianadda de Martigny. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 5, Martigny, Valais, Suisse',
    46.1042689990162,
    7.0637348462170175,
    '2026-03-21',
    '10:30:00',
    '2026-03-21',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.martigny.ch/agenda/event-5932',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show - Édition 2026',
    'Découvrez one-man show au/à la W Hotel de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 22, Verbier, Valais, Suisse',
    46.09616642751938,
    7.233428495572347,
    '2026-03-21',
    '17:30:00',
    '2026-03-21',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-8066',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel - Printemps 2026',
    'La commune de Brig vous invite à salon professionnel. Rendez-vous au/à la Stockalperschloss pour un moment exceptionnel.',
    'Place Centrale 15, Brig, Valais, Suisse',
    46.31490053152471,
    7.986633715776936,
    '2026-03-22',
    '19:00:00',
    '2026-03-22',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.brig.ch/agenda/event-7801',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical au Hôtel de Anzère',
    'Brunch musical organisé(e) au/à la Hôtel de Anzère, Anzère. Événement ouvert à tous, petits et grands.',
    'Place Centrale 23, Anzère, Valais, Suisse',
    46.29496494769829,
    7.401273929702945,
    '2026-03-23',
    '09:30:00',
    '2026-03-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.anzère.ch/agenda/event-7840',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Édition 2026',
    'Rendez-vous à Zermatt pour marché gourmand. Cet événement se tiendra au/à la Église de Zermatt. Ne manquez pas cette occasion unique!',
    'Route Cantonale 14, Zermatt, Valais, Suisse',
    46.01802224215771,
    7.752641675291911,
    '2026-03-23',
    '08:30:00',
    '2026-03-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4864',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée au Thermalquellen',
    'La commune de Leukerbad vous invite à randonnée guidée. Rendez-vous au/à la Thermalquellen pour un moment exceptionnel.',
    'Avenue de la Gare 37, Leukerbad, Valais, Suisse',
    46.37986491427354,
    7.629283633035693,
    '2026-03-25',
    '18:30:00',
    '2026-03-25',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.leukerbad.ch/agenda/event-4090',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Printemps 2026',
    'Rendez-vous à Nendaz pour marché de printemps. Cet événement se tiendra au/à la Salle polyvalente. Ne manquez pas cette occasion unique!',
    'Place Centrale 34, Nendaz, Valais, Suisse',
    46.188058946388416,
    7.30064949610869,
    '2026-03-26',
    '08:00:00',
    '2026-03-26',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-7852',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art à Salvan',
    'Exposition d''art organisé(e) au/à la Château de Salvan, Salvan. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 9, Salvan, Valais, Suisse',
    46.11284438697453,
    7.013672391083396,
    '2026-03-27',
    '17:30:00',
    '2026-03-27',
    '["Culture > Expositions"]'::jsonb,
    'https://www.salvan.ch/agenda/event-2422',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée à Zermatt',
    'Randonnée guidée organisé(e) au/à la Salle Communale, Zermatt. Événement ouvert à tous, petits et grands.',
    'Place Centrale 14, Zermatt, Valais, Suisse',
    46.019447063319376,
    7.747936293011181,
    '2026-03-31',
    '17:00:00',
    '2026-03-31',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-9296',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail',
    'Martigny accueille trail le 01 April 2026. Venez nombreux au/à la Manoir de la Ville!',
    'Place Centrale 27, Martigny, Valais, Suisse',
    46.103927651403495,
    7.066098354929712,
    '2026-04-01',
    '14:00:00',
    '2026-04-01',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-4774',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Brig',
    'Rendez-vous à Brig pour marché de printemps. Cet événement se tiendra au/à la Stockalperschloss. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 47, Brig, Valais, Suisse',
    46.31700810896554,
    7.983543085620114,
    '2026-04-01',
    '08:00:00',
    '2026-04-01',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.brig.ch/agenda/event-6142',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show à Ayent',
    'Rendez-vous à Ayent pour one-man show. Cet événement se tiendra au/à la Théâtre de Ayent. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 21, Ayent, Valais, Suisse',
    46.287111962391954,
    7.417499045064818,
    '2026-04-01',
    '10:30:00',
    '2026-04-01',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.ayent.ch/agenda/event-7860',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz - Printemps 2026',
    'Concert Jazz organisé(e) au/à la La Poste Culture, Visp. Événement ouvert à tous, petits et grands.',
    'Place Centrale 42, Visp, Valais, Suisse',
    46.29422939015885,
    7.879719924004546,
    '2026-04-04',
    '21:30:00',
    '2026-04-04',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.visp.ch/agenda/event-3288',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel',
    'Découvrez salon professionnel au/à la La Poste Culture de Visp. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 42, Visp, Valais, Suisse',
    46.29212456382842,
    7.885955947228466,
    '2026-04-04',
    '20:30:00',
    '2026-04-04',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-9020',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin - Édition 2026',
    'Sierre accueille dégustation de vin le 04 April 2026. Venez nombreux au/à la Château de Villa!',
    'Rue de l''Église 8, Sierre, Valais, Suisse',
    46.29320603365226,
    7.5392897150646005,
    '2026-04-04',
    '19:00:00',
    '2026-04-04',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.sierre.ch/agenda/event-4714',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage - Édition 2026',
    'Rendez-vous à Brig pour vernissage. Cet événement se tiendra au/à la Stockalperschloss. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 16, Brig, Valais, Suisse',
    46.316164989804165,
    7.985468867754354,
    '2026-04-07',
    '15:30:00',
    '2026-04-07',
    '["Culture > Expositions"]'::jsonb,
    'https://www.brig.ch/agenda/event-1487',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto',
    'Verbier accueille loto le 07 April 2026. Venez nombreux au/à la Église de Verbier!',
    'Rue de l''Église 30, Verbier, Valais, Suisse',
    46.09679518294432,
    7.226136490201167,
    '2026-04-07',
    '10:00:00',
    '2026-04-07',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.verbier.ch/agenda/event-6681',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Salle Communale',
    'Fête de village organisé(e) au/à la Salle Communale, Monthey. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 46, Monthey, Valais, Suisse',
    46.25144068585019,
    6.945119230804283,
    '2026-04-10',
    '10:30:00',
    '2026-04-10',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.monthey.ch/agenda/event-3498',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale - Martigny',
    'Martigny accueille comédie musicale le 10 April 2026. Venez nombreux au/à la Manoir de la Ville!',
    'Chemin des Vignes 6, Martigny, Valais, Suisse',
    46.09513580932583,
    7.062136172954796,
    '2026-04-10',
    '17:30:00',
    '2026-04-10',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-5295',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante au Place de Champéry',
    'Champéry accueille brocante le 10 April 2026. Venez nombreux au/à la Place de Champéry!',
    'Rue du Bourg 35, Champéry, Valais, Suisse',
    46.17708253495083,
    6.8650692757549425,
    '2026-04-10',
    '08:00:00',
    '2026-04-10',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.champéry.ch/agenda/event-2483',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage à Zermatt',
    'Vernissage organisé(e) au/à la Vernissage Hotel, Zermatt. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 18, Zermatt, Valais, Suisse',
    46.018535251970064,
    7.74534129022154,
    '2026-04-12',
    '18:30:00',
    '2026-04-12',
    '["Culture > Expositions"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2558',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village - Édition 2026',
    'Fête de village organisé(e) au/à la Régent Palace, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Place Centrale 28, Crans-Montana, Valais, Suisse',
    46.309707529861264,
    7.484576380576281,
    '2026-04-13',
    '17:30:00',
    '2026-04-13',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-2700',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz - Édition 2026',
    'Concert Jazz organisé(e) au/à la Casino Crans-Montana, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 48, Crans-Montana, Valais, Suisse',
    46.308994895517955,
    7.480158748618133,
    '2026-04-13',
    '19:30:00',
    '2026-04-13',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-3839',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art',
    'Sion accueille exposition d''art le 14 April 2026. Venez nombreux au/à la Théâtre de Valère!',
    'Rue de l''Église 20, Sion, Valais, Suisse',
    46.23318530548795,
    7.364810308429926,
    '2026-04-14',
    '14:00:00',
    '2026-04-14',
    '["Culture > Expositions"]'::jsonb,
    'https://www.sion.ch/agenda/event-7224',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Verbier',
    'Verbier accueille compétition de ski le 15 April 2026. Venez nombreux au/à la W Hotel!',
    'Rue de l''Église 23, Verbier, Valais, Suisse',
    46.10104700809409,
    7.233063021114369,
    '2026-04-15',
    '18:30:00',
    '2026-04-15',
    '["Sport > Glisse"]'::jsonb,
    'https://www.verbier.ch/agenda/event-6976',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence au Bibliothèque de Ayent',
    'Découvrez conférence au/à la Bibliothèque de Ayent de Ayent. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 31, Ayent, Valais, Suisse',
    46.280555427279644,
    7.413619025084719,
    '2026-04-17',
    '17:00:00',
    '2026-04-17',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.ayent.ch/agenda/event-7452',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ au Centre Sportif',
    'Découvrez soirée dj au/à la Centre Sportif de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 42, Verbier, Valais, Suisse',
    46.09330074974818,
    7.230036877426431,
    '2026-04-18',
    '21:00:00',
    '2026-04-18',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.verbier.ch/agenda/event-8685',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show - Édition 2026',
    'La commune de Martigny vous invite à one-man show. Rendez-vous au/à la Fondation Gianadda pour un moment exceptionnel.',
    'Rue de l''Église 14, Martigny, Valais, Suisse',
    46.0970375981287,
    7.068210670536596,
    '2026-04-18',
    '17:30:00',
    '2026-04-18',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-1467',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Édition 2026',
    'Rendez-vous à Zermatt pour marché de printemps. Cet événement se tiendra au/à la Vernissage Hotel. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 15, Zermatt, Valais, Suisse',
    46.02485880790769,
    7.7494403887289645,
    '2026-04-19',
    '08:00:00',
    '2026-04-19',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-6346',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski à Monthey',
    'Découvrez compétition de ski au/à la Salle Communale de Monthey. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 10, Monthey, Valais, Suisse',
    46.252256521196266,
    6.953563001048694,
    '2026-04-20',
    '20:00:00',
    '2026-04-20',
    '["Sport > Glisse"]'::jsonb,
    'https://www.monthey.ch/agenda/event-6163',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage',
    'Rendez-vous à Martigny pour vernissage. Cet événement se tiendra au/à la Fondation Gianadda. Ne manquez pas cette occasion unique!',
    'Place Centrale 17, Martigny, Valais, Suisse',
    46.10105127683657,
    7.066136396722823,
    '2026-04-20',
    '10:00:00',
    '2026-04-20',
    '["Culture > Expositions"]'::jsonb,
    'https://www.martigny.ch/agenda/event-3003',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey',
    'Match de hockey organisé(e) au/à la Aréna de Grimentz, Grimentz. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 39, Grimentz, Valais, Suisse',
    46.183303330103044,
    7.578206377471323,
    '2026-04-21',
    '15:30:00',
    '2026-04-21',
    '["Sport > Glisse"]'::jsonb,
    'https://www.grimentz.ch/agenda/event-6476',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail au Caves Varone',
    'La commune de Sion vous invite à trail. Rendez-vous au/à la Caves Varone pour un moment exceptionnel.',
    'Rue du Bourg 4, Sion, Valais, Suisse',
    46.23096214325661,
    7.368098671391009,
    '2026-04-22',
    '20:00:00',
    '2026-04-22',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-8230',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Édition 2026',
    'Découvrez spectacle de théâtre au/à la Centre thermal de Leukerbad. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 35, Leukerbad, Valais, Suisse',
    46.37811320088019,
    7.622000852437141,
    '2026-04-22',
    '10:30:00',
    '2026-04-22',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.leukerbad.ch/agenda/event-1330',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show',
    'One-man show organisé(e) au/à la Casino de Sion, Sion. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 42, Sion, Valais, Suisse',
    46.23508919259468,
    7.3623712815700975,
    '2026-04-22',
    '20:30:00',
    '2026-04-22',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.sion.ch/agenda/event-4681',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand à Chamoson',
    'Rendez-vous à Chamoson pour marché gourmand. Cet événement se tiendra au/à la Place de Chamoson. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 2, Chamoson, Valais, Suisse',
    46.20257584525053,
    7.220673141618608,
    '2026-04-22',
    '08:00:00',
    '2026-04-22',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-8531',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif au La Poste Culture',
    'Rendez-vous à Visp pour atelier créatif. Cet événement se tiendra au/à la La Poste Culture. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 22, Visp, Valais, Suisse',
    46.296214303266424,
    7.884340422081961,
    '2026-04-22',
    '10:30:00',
    '2026-04-22',
    '["Culture > Workshops"]'::jsonb,
    'https://www.visp.ch/agenda/event-5634',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski au Golf de Crans',
    'Compétition de ski organisé(e) au/à la Golf de Crans, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 41, Crans-Montana, Valais, Suisse',
    46.307611792408785,
    7.477237631382255,
    '2026-04-25',
    '15:00:00',
    '2026-04-25',
    '["Sport > Glisse"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-8570',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Printemps 2026',
    'Exposition d''art organisé(e) au/à la Galerie de Saint-Maurice, Saint-Maurice. Événement ouvert à tous, petits et grands.',
    'Place Centrale 24, Saint-Maurice, Valais, Suisse',
    46.22162474186147,
    7.00176782813611,
    '2026-04-26',
    '20:30:00',
    '2026-04-26',
    '["Culture > Expositions"]'::jsonb,
    'https://www.saintmaurice.ch/agenda/event-9975',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique au CERM',
    'Martigny accueille concert de musique classique le 27 April 2026. Venez nombreux au/à la CERM!',
    'Rue du Rhône 14, Martigny, Valais, Suisse',
    46.0984410563093,
    7.065042065041026,
    '2026-04-27',
    '21:30:00',
    '2026-04-27',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.martigny.ch/agenda/event-9827',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking - Martigny',
    'La commune de Martigny vous invite à networking. Rendez-vous au/à la Caves Orsat pour un moment exceptionnel.',
    'Place Centrale 43, Martigny, Valais, Suisse',
    46.09562551813272,
    7.071360188802724,
    '2026-04-30',
    '10:30:00',
    '2026-04-30',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.martigny.ch/agenda/event-1870',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Édition 2026',
    'Atelier créatif organisé(e) au/à la Centre Sportif, Verbier. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 28, Verbier, Valais, Suisse',
    46.094957619763896,
    7.225897688046251,
    '2026-04-30',
    '20:30:00',
    '2026-04-30',
    '["Culture > Workshops"]'::jsonb,
    'https://www.verbier.ch/agenda/event-6499',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert à Chamoson',
    'Rendez-vous à Chamoson pour concert. Cet événement se tiendra au/à la Théâtre de Chamoson. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 27, Chamoson, Valais, Suisse',
    46.204091791354145,
    7.215933030708987,
    '2026-05-01',
    '21:00:00',
    '2026-05-01',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-5126',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin à Champéry',
    'Champéry accueille dégustation de vin le 02 May 2026. Venez nombreux au/à la Cave de Champéry!',
    'Rue de l''Église 9, Champéry, Valais, Suisse',
    46.17678140739415,
    6.86716820240673,
    '2026-05-02',
    '15:30:00',
    '2026-05-02',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.champéry.ch/agenda/event-4007',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Course populaire au Théâtre La Poste',
    'Course populaire organisé(e) au/à la Théâtre La Poste, Visp. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 48, Visp, Valais, Suisse',
    46.29830062574612,
    7.880572578734314,
    '2026-05-02',
    '15:00:00',
    '2026-05-02',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.visp.ch/agenda/event-2432',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz - Printemps 2026',
    'Rendez-vous à Crans-Montana pour concert jazz. Cet événement se tiendra au/à la Casino Crans-Montana. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 40, Crans-Montana, Valais, Suisse',
    46.309472211974445,
    7.482934193185668,
    '2026-05-02',
    '21:30:00',
    '2026-05-02',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-3272',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique à Verbier',
    'Découvrez festival de musique au/à la Salle des Combins de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 45, Verbier, Valais, Suisse',
    46.0932865310653,
    7.224998576444934,
    '2026-05-05',
    '22:00:00',
    '2026-05-07',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-1278',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical au Église de Verbier',
    'La commune de Verbier vous invite à brunch musical. Rendez-vous au/à la Église de Verbier pour un moment exceptionnel.',
    'Rue du Bourg 50, Verbier, Valais, Suisse',
    46.098972619254546,
    7.228238188237276,
    '2026-05-06',
    '10:00:00',
    '2026-05-06',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.verbier.ch/agenda/event-3892',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey à Leytron',
    'La commune de Leytron vous invite à match de hockey. Rendez-vous au/à la Aréna de Leytron pour un moment exceptionnel.',
    'Rue du Bourg 28, Leytron, Valais, Suisse',
    46.18418777729836,
    7.202003561985626,
    '2026-05-07',
    '19:00:00',
    '2026-05-07',
    '["Sport > Glisse"]'::jsonb,
    'https://www.leytron.ch/agenda/event-5734',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert',
    'Rendez-vous à Sion pour concert. Cet événement se tiendra au/à la Place de la Planta. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 5, Sion, Valais, Suisse',
    46.23085215953827,
    7.371543356391939,
    '2026-05-07',
    '20:30:00',
    '2026-05-07',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.sion.ch/agenda/event-4389',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking - Édition 2026',
    'Networking organisé(e) au/à la Fondation Gianadda, Martigny. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 26, Martigny, Valais, Suisse',
    46.10108482389306,
    7.066001115090803,
    '2026-05-08',
    '19:00:00',
    '2026-05-08',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.martigny.ch/agenda/event-8004',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Brig',
    'Rendez-vous à Brig pour atelier créatif. Cet événement se tiendra au/à la Centre Culturel. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 30, Brig, Valais, Suisse',
    46.31717474092505,
    7.9876979845029314,
    '2026-05-09',
    '17:00:00',
    '2026-05-09',
    '["Culture > Workshops"]'::jsonb,
    'https://www.brig.ch/agenda/event-9442',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Édition 2026',
    'La commune de Sierre vous invite à atelier créatif. Rendez-vous au/à la Salle de Borzuat pour un moment exceptionnel.',
    'Avenue de la Gare 7, Sierre, Valais, Suisse',
    46.29007908120049,
    7.534124101624392,
    '2026-05-09',
    '15:00:00',
    '2026-05-09',
    '["Culture > Workshops"]'::jsonb,
    'https://www.sierre.ch/agenda/event-9264',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Printemps 2026',
    'La commune de Sierre vous invite à concert de musique classique. Rendez-vous au/à la Caves du Paradis pour un moment exceptionnel.',
    'Avenue de la Gare 3, Sierre, Valais, Suisse',
    46.2879040657789,
    7.530733494106482,
    '2026-05-10',
    '21:30:00',
    '2026-05-10',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.sierre.ch/agenda/event-3167',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical - Édition 2026',
    'La commune de Ovronnaz vous invite à brunch musical. Rendez-vous au/à la Restaurant de Ovronnaz pour un moment exceptionnel.',
    'Rue du Rhône 26, Ovronnaz, Valais, Suisse',
    46.19104035248048,
    7.168881098118259,
    '2026-05-10',
    '10:30:00',
    '2026-05-10',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-1466',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art à Crans-Montana',
    'Découvrez exposition d''art au/à la Centre de Congrès le Régent de Crans-Montana. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Bourg 45, Crans-Montana, Valais, Suisse',
    46.30438825004209,
    7.479039805391547,
    '2026-05-10',
    '20:00:00',
    '2026-05-10',
    '["Culture > Expositions"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-2263',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail au Simplonhalle',
    'Brig accueille trail le 11 May 2026. Venez nombreux au/à la Simplonhalle!',
    'Rue de l''Église 9, Brig, Valais, Suisse',
    46.31367332866712,
    7.984236972451551,
    '2026-05-11',
    '20:30:00',
    '2026-05-11',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.brig.ch/agenda/event-9231',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Sion',
    'Atelier créatif organisé(e) au/à la Caves Varone, Sion. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 15, Sion, Valais, Suisse',
    46.2321456850721,
    7.370722108088246,
    '2026-05-11',
    '14:00:00',
    '2026-05-11',
    '["Culture > Workshops"]'::jsonb,
    'https://www.sion.ch/agenda/event-4721',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking à Zermatt',
    'Rendez-vous à Zermatt pour networking. Cet événement se tiendra au/à la Salle Communale. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 3, Zermatt, Valais, Suisse',
    46.02378765545488,
    7.749285291870159,
    '2026-05-12',
    '18:00:00',
    '2026-05-12',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-5417',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif à Savièse',
    'Savièse accueille atelier créatif le 13 May 2026. Venez nombreux au/à la Atelier de Savièse!',
    'Rue du Bourg 37, Savièse, Valais, Suisse',
    46.24601354854041,
    7.3518373479049925,
    '2026-05-13',
    '18:30:00',
    '2026-05-13',
    '["Culture > Workshops"]'::jsonb,
    'https://www.savièse.ch/agenda/event-3460',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert - Édition 2026',
    'Concert organisé(e) au/à la Église de Zermatt, Zermatt. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 28, Zermatt, Valais, Suisse',
    46.02100392485131,
    7.750277206233336,
    '2026-05-14',
    '19:30:00',
    '2026-05-14',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-6495',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ',
    'Monthey accueille soirée dj le 14 May 2026. Venez nombreux au/à la Salle Communale!',
    'Place Centrale 48, Monthey, Valais, Suisse',
    46.249744879342956,
    6.951010183183317,
    '2026-05-14',
    '21:00:00',
    '2026-05-14',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.monthey.ch/agenda/event-4242',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand au Caves du Paradis',
    'La commune de Sierre vous invite à marché gourmand. Rendez-vous au/à la Caves du Paradis pour un moment exceptionnel.',
    'Rue de l''Église 12, Sierre, Valais, Suisse',
    46.29087755890245,
    7.532871400852404,
    '2026-05-16',
    '10:00:00',
    '2026-05-16',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.sierre.ch/agenda/event-6469',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz',
    'La commune de Salvan vous invite à soirée quiz. Rendez-vous au/à la Pub de Salvan pour un moment exceptionnel.',
    'Rue du Bourg 46, Salvan, Valais, Suisse',
    46.11961852437265,
    7.0206335739313275,
    '2026-05-16',
    '19:00:00',
    '2026-05-16',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.salvan.ch/agenda/event-4762',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical au Hôtel de Leytron',
    'Leytron accueille brunch musical le 19 May 2026. Venez nombreux au/à la Hôtel de Leytron!',
    'Place Centrale 4, Leytron, Valais, Suisse',
    46.18810619039442,
    7.200827072294982,
    '2026-05-19',
    '11:00:00',
    '2026-05-19',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.leytron.ch/agenda/event-5519',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage',
    'Leytron accueille vernissage le 20 May 2026. Venez nombreux au/à la Galerie de Leytron!',
    'Rue du Bourg 29, Leytron, Valais, Suisse',
    46.180512930301795,
    7.20287815338504,
    '2026-05-20',
    '15:30:00',
    '2026-05-20',
    '["Culture > Expositions"]'::jsonb,
    'https://www.leytron.ch/agenda/event-5413',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey à Fully',
    'Match de hockey organisé(e) au/à la Aréna de Fully, Fully. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 46, Fully, Valais, Suisse',
    46.131376511992244,
    7.118964925950511,
    '2026-05-21',
    '19:30:00',
    '2026-05-21',
    '["Sport > Glisse"]'::jsonb,
    'https://www.fully.ch/agenda/event-5547',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Édition 2026',
    'Rendez-vous à Leytron pour marché de printemps. Cet événement se tiendra au/à la Marché de Leytron. Ne manquez pas cette occasion unique!',
    'Route Cantonale 19, Leytron, Valais, Suisse',
    46.18234167078766,
    7.201012765932282,
    '2026-05-21',
    '10:30:00',
    '2026-05-21',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.leytron.ch/agenda/event-4370',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz à Sion',
    'Sion accueille soirée quiz le 22 May 2026. Venez nombreux au/à la Salle de la Matze!',
    'Rue du Bourg 50, Sion, Valais, Suisse',
    46.23603028016862,
    7.363327217692002,
    '2026-05-22',
    '20:00:00',
    '2026-05-22',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.sion.ch/agenda/event-3378',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Édition 2026',
    'Savièse accueille marché de printemps le 22 May 2026. Venez nombreux au/à la Place de Savièse!',
    'Rue du Bourg 38, Savièse, Valais, Suisse',
    46.253571069081744,
    7.3452573073549665,
    '2026-05-22',
    '10:00:00',
    '2026-05-22',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.savièse.ch/agenda/event-7879',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert',
    'Découvrez concert au/à la Place de Evolène de Evolène. Un moment convivial à partager en famille ou entre amis.',
    'Rue de l''Église 2, Evolène, Valais, Suisse',
    46.116638159016524,
    7.488170440708736,
    '2026-05-22',
    '20:00:00',
    '2026-05-22',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.evolène.ch/agenda/event-6502',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Printemps 2026',
    'Découvrez marché gourmand au/à la Place de Leytron de Leytron. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 24, Leytron, Valais, Suisse',
    46.17970113562185,
    7.19564371963918,
    '2026-05-22',
    '09:30:00',
    '2026-05-22',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.leytron.ch/agenda/event-6766',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage - Édition 2026',
    'Vernissage organisé(e) au/à la Église de Zermatt, Zermatt. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 41, Zermatt, Valais, Suisse',
    46.02228230679294,
    7.749808369842559,
    '2026-05-23',
    '15:30:00',
    '2026-05-23',
    '["Culture > Expositions"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-8467',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps au Télécabine',
    'La commune de Nendaz vous invite à marché de printemps. Rendez-vous au/à la Télécabine pour un moment exceptionnel.',
    'Place Centrale 37, Nendaz, Valais, Suisse',
    46.18448767205595,
    7.301927168334988,
    '2026-05-24',
    '10:00:00',
    '2026-05-24',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-7197',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée',
    'La commune de Monthey vous invite à randonnée guidée. Rendez-vous au/à la Théâtre du Crochetan pour un moment exceptionnel.',
    'Chemin des Vignes 24, Monthey, Valais, Suisse',
    46.25189147584906,
    6.9499000561595174,
    '2026-05-25',
    '10:30:00',
    '2026-05-25',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.monthey.ch/agenda/event-1885',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Édition 2026',
    'Découvrez concert de musique classique au/à la Médiathèque Valais de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 49, Sion, Valais, Suisse',
    46.229269460469425,
    7.366881946374361,
    '2026-05-25',
    '22:30:00',
    '2026-05-25',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.sion.ch/agenda/event-1339',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Édition 2026',
    'Spectacle de théâtre organisé(e) au/à la Théâtre de Ayent, Ayent. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 8, Ayent, Valais, Suisse',
    46.28183561858215,
    7.41812980499509,
    '2026-05-25',
    '17:00:00',
    '2026-05-25',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.ayent.ch/agenda/event-2948',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale au Manoir de la Ville',
    'Comédie musicale organisé(e) au/à la Manoir de la Ville, Martigny. Événement ouvert à tous, petits et grands.',
    'Place Centrale 10, Martigny, Valais, Suisse',
    46.101801109496385,
    7.062598822869547,
    '2026-05-25',
    '14:30:00',
    '2026-05-25',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-9521',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert - Printemps 2026',
    'Rendez-vous à Savièse pour concert. Cet événement se tiendra au/à la Salle de Savièse. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 36, Savièse, Valais, Suisse',
    46.24869846869867,
    7.349596531003894,
    '2026-05-26',
    '21:00:00',
    '2026-05-26',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.savièse.ch/agenda/event-4078',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Printemps 2026',
    'La commune de Ardon vous invite à soirée dj. Rendez-vous au/à la Bar de Ardon pour un moment exceptionnel.',
    'Rue de l''Église 36, Ardon, Valais, Suisse',
    46.19759794461773,
    7.2527440955128215,
    '2026-05-27',
    '20:30:00',
    '2026-05-27',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.ardon.ch/agenda/event-6376',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art',
    'Zermatt accueille exposition d''art le 29 May 2026. Venez nombreux au/à la Salle Communale!',
    'Rue du Rhône 10, Zermatt, Valais, Suisse',
    46.01833201371851,
    7.753397622357627,
    '2026-05-29',
    '10:00:00',
    '2026-05-29',
    '["Culture > Expositions"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-7699',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Salle polyvalente',
    'Fête de village organisé(e) au/à la Salle polyvalente, Nendaz. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 45, Nendaz, Valais, Suisse',
    46.18057715041928,
    7.302398989428819,
    '2026-05-30',
    '10:30:00',
    '2026-05-30',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-4195',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Visp',
    'La commune de Visp vous invite à spectacle de théâtre. Rendez-vous au/à la Théâtre La Poste pour un moment exceptionnel.',
    'Rue du Rhône 33, Visp, Valais, Suisse',
    46.29420845464145,
    7.884236589956064,
    '2026-06-02',
    '19:30:00',
    '2026-06-02',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.visp.ch/agenda/event-8214',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Zermatt',
    'La commune de Zermatt vous invite à spectacle de théâtre. Rendez-vous au/à la Salle Communale pour un moment exceptionnel.',
    'Avenue de la Gare 13, Zermatt, Valais, Suisse',
    46.023780625326204,
    7.750465763544443,
    '2026-06-03',
    '18:00:00',
    '2026-06-03',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4824',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Martigny',
    'Rendez-vous à Martigny pour exposition d''art. Cet événement se tiendra au/à la Manoir de la Ville. Ne manquez pas cette occasion unique!',
    'Route Cantonale 50, Martigny, Valais, Suisse',
    46.09914099562784,
    7.068025388468732,
    '2026-06-04',
    '15:00:00',
    '2026-06-04',
    '["Culture > Expositions"]'::jsonb,
    'https://www.martigny.ch/agenda/event-8578',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps au Château de Tourbillon',
    'Marché de printemps organisé(e) au/à la Château de Tourbillon, Sion. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 48, Sion, Valais, Suisse',
    46.23003837078516,
    7.3699684068347,
    '2026-06-05',
    '10:30:00',
    '2026-06-05',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sion.ch/agenda/event-1057',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Vernissage Hotel',
    'Rendez-vous à Zermatt pour fête de village. Cet événement se tiendra au/à la Vernissage Hotel. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 7, Zermatt, Valais, Suisse',
    46.02052004373843,
    7.750974770524628,
    '2026-06-06',
    '19:00:00',
    '2026-06-06',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-3616',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Printemps 2026',
    'Trail organisé(e) au/à la Départ de Ardon, Ardon. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 24, Ardon, Valais, Suisse',
    46.198330823300104,
    7.245022130894095,
    '2026-06-06',
    '17:30:00',
    '2026-06-06',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.ardon.ch/agenda/event-1786',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey',
    'Match de hockey organisé(e) au/à la Château de Villa, Sierre. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 10, Sierre, Valais, Suisse',
    46.29487361008833,
    7.537731479008243,
    '2026-06-06',
    '17:30:00',
    '2026-06-06',
    '["Sport > Glisse"]'::jsonb,
    'https://www.sierre.ch/agenda/event-4877',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz - Édition 2026',
    'Concert Jazz organisé(e) au/à la Bar de Grimentz, Grimentz. Événement ouvert à tous, petits et grands.',
    'Place Centrale 21, Grimentz, Valais, Suisse',
    46.179107380568276,
    7.5756619890911905,
    '2026-06-08',
    '21:00:00',
    '2026-06-08',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.grimentz.ch/agenda/event-8308',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film - Printemps 2026',
    'Projection de film organisé(e) au/à la Forum Claudel, Martigny. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 49, Martigny, Valais, Suisse',
    46.101311442764796,
    7.065230208111895,
    '2026-06-10',
    '19:00:00',
    '2026-06-10',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.martigny.ch/agenda/event-8346',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Édition 2026',
    'La commune de Nendaz vous invite à randonnée guidée. Rendez-vous au/à la Centre sportif pour un moment exceptionnel.',
    'Place Centrale 28, Nendaz, Valais, Suisse',
    46.18474498920807,
    7.297896947360259,
    '2026-06-11',
    '15:00:00',
    '2026-06-11',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-8804',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking à Conthey',
    'Networking organisé(e) au/à la Restaurant de Conthey, Conthey. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 24, Conthey, Valais, Suisse',
    46.220192857092094,
    7.295176614986135,
    '2026-06-12',
    '14:00:00',
    '2026-06-12',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.conthey.ch/agenda/event-2691',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante à Verbier',
    'Découvrez brocante au/à la Église de Verbier de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Rue de l''Église 10, Verbier, Valais, Suisse',
    46.09451362485045,
    7.230351371203482,
    '2026-06-13',
    '10:30:00',
    '2026-06-13',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-3884',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Nendaz',
    'Concert de musique classique organisé(e) au/à la Salle polyvalente, Nendaz. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 5, Nendaz, Valais, Suisse',
    46.18313640479838,
    7.304719681361295,
    '2026-06-14',
    '20:30:00',
    '2026-06-14',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-9259',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz - Printemps 2026',
    'Rendez-vous à Ardon pour soirée quiz. Cet événement se tiendra au/à la Bar de Ardon. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 39, Ardon, Valais, Suisse',
    46.197909888767924,
    7.251247954281743,
    '2026-06-15',
    '19:30:00',
    '2026-06-15',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.ardon.ch/agenda/event-3052',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical au Église de Saas-Fee',
    'Découvrez brunch musical au/à la Église de Saas-Fee de Saas-Fee. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 19, Saas-Fee, Valais, Suisse',
    46.10811299848727,
    7.930797883326198,
    '2026-06-18',
    '10:00:00',
    '2026-06-18',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.saasfee.ch/agenda/event-4684',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Édition 2026',
    'La commune de Leytron vous invite à marché de printemps. Rendez-vous au/à la Place de Leytron pour un moment exceptionnel.',
    'Chemin des Vignes 13, Leytron, Valais, Suisse',
    46.185573265752936,
    7.201242004291696,
    '2026-06-18',
    '10:00:00',
    '2026-06-18',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.leytron.ch/agenda/event-2747',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ',
    'Soirée DJ organisé(e) au/à la Salle de la Matze, Sion. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 6, Sion, Valais, Suisse',
    46.23502829758451,
    7.3709580237441905,
    '2026-06-19',
    '21:30:00',
    '2026-06-19',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.sion.ch/agenda/event-9503',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert au Salle des Combins',
    'La commune de Verbier vous invite à concert. Rendez-vous au/à la Salle des Combins pour un moment exceptionnel.',
    'Avenue de la Gare 26, Verbier, Valais, Suisse',
    46.0939859969923,
    7.227410225304226,
    '2026-06-21',
    '22:30:00',
    '2026-06-21',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5748',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz à Crans-Montana',
    'Crans-Montana accueille concert jazz le 24 June 2026. Venez nombreux au/à la Golf de Crans!',
    'Rue du Rhône 47, Crans-Montana, Valais, Suisse',
    46.30776361715134,
    7.481761720656417,
    '2026-06-24',
    '21:30:00',
    '2026-06-24',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-8308',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Printemps 2026',
    'Trail organisé(e) au/à la Vernissage Hotel, Zermatt. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 11, Zermatt, Valais, Suisse',
    46.018450960571805,
    7.74810505433544,
    '2026-06-26',
    '15:00:00',
    '2026-06-26',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-8965',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale au Salle de Borzuat',
    'Rendez-vous à Sierre pour comédie musicale. Cet événement se tiendra au/à la Salle de Borzuat. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 48, Sierre, Valais, Suisse',
    46.29492366381207,
    7.530557190452709,
    '2026-06-28',
    '14:00:00',
    '2026-06-28',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.sierre.ch/agenda/event-2298',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique à Sierre',
    'Découvrez festival de musique au/à la Fondation Rilke de Sierre. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Bourg 1, Sierre, Valais, Suisse',
    46.28834823238238,
    7.533368191348641,
    '2026-06-28',
    '20:30:00',
    '2026-06-30',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.sierre.ch/agenda/event-4427',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence - Brig',
    'Conférence organisé(e) au/à la Centre Culturel, Brig. Événement ouvert à tous, petits et grands.',
    'Place Centrale 33, Brig, Valais, Suisse',
    46.31403978842902,
    7.9832362145425515,
    '2026-06-28',
    '19:00:00',
    '2026-06-28',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.brig.ch/agenda/event-4288',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Ardon',
    'Découvrez exposition d''art au/à la Château de Ardon de Ardon. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 48, Ardon, Valais, Suisse',
    46.20055495049997,
    7.249927197194453,
    '2026-06-29',
    '10:00:00',
    '2026-06-29',
    '["Culture > Expositions"]'::jsonb,
    'https://www.ardon.ch/agenda/event-8208',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking - Printemps 2026',
    'Rendez-vous à Nendaz pour networking. Cet événement se tiendra au/à la Centre sportif. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 28, Nendaz, Valais, Suisse',
    46.18261252785186,
    7.296967524299031,
    '2026-06-29',
    '10:00:00',
    '2026-06-29',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-3376',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Édition 2026',
    'La commune de Martigny vous invite à randonnée guidée. Rendez-vous au/à la Fondation Gianadda pour un moment exceptionnel.',
    'Rue du Bourg 49, Martigny, Valais, Suisse',
    46.10016965345965,
    7.066058440540284,
    '2026-06-30',
    '15:00:00',
    '2026-06-30',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-1803',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel - Champéry',
    'Champéry accueille salon professionnel le 01 July 2026. Venez nombreux au/à la Centre De Congrès de Champéry!',
    'Rue de l''Église 12, Champéry, Valais, Suisse',
    46.17780844421758,
    6.873290725449755,
    '2026-07-01',
    '14:30:00',
    '2026-07-01',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.champéry.ch/agenda/event-4865',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval',
    'Découvrez carnaval au/à la Place de l''Hôtel de Ville de Monthey. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 1, Monthey, Valais, Suisse',
    46.25356545360457,
    6.949323675025125,
    '2026-07-01',
    '18:30:00',
    '2026-07-01',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.monthey.ch/agenda/event-3218',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand',
    'Brig accueille marché gourmand le 04 July 2026. Venez nombreux au/à la Simplonhalle!',
    'Route Cantonale 21, Brig, Valais, Suisse',
    46.3137700346267,
    7.983481296413816,
    '2026-07-04',
    '10:00:00',
    '2026-07-04',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.brig.ch/agenda/event-2530',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Printemps 2026',
    'La commune de Brig vous invite à spectacle de théâtre. Rendez-vous au/à la Centre Culturel pour un moment exceptionnel.',
    'Rue du Rhône 50, Brig, Valais, Suisse',
    46.31231834682203,
    7.98430948299693,
    '2026-07-04',
    '10:00:00',
    '2026-07-04',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.brig.ch/agenda/event-7582',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking',
    'La commune de Martigny vous invite à networking. Rendez-vous au/à la CERM pour un moment exceptionnel.',
    'Rue du Rhône 29, Martigny, Valais, Suisse',
    46.09744896928342,
    7.069436428420933,
    '2026-07-05',
    '20:00:00',
    '2026-07-05',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.martigny.ch/agenda/event-4123',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand au Vernissage Hotel',
    'Marché gourmand organisé(e) au/à la Vernissage Hotel, Zermatt. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 6, Zermatt, Valais, Suisse',
    46.01798170861858,
    7.7442064287853976,
    '2026-07-06',
    '09:00:00',
    '2026-07-06',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2531',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey - Nendaz',
    'Nendaz accueille match de hockey le 07 July 2026. Venez nombreux au/à la Centre sportif!',
    'Route Cantonale 27, Nendaz, Valais, Suisse',
    46.182123555408815,
    7.301781046582854,
    '2026-07-07',
    '20:30:00',
    '2026-07-07',
    '["Sport > Glisse"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-4542',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Verbier',
    'Découvrez spectacle de théâtre au/à la Centre Sportif de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 29, Verbier, Valais, Suisse',
    46.09400504694163,
    7.226119986755587,
    '2026-07-08',
    '19:00:00',
    '2026-07-08',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-6251',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto - Printemps 2026',
    'La commune de Crans-Montana vous invite à loto. Rendez-vous au/à la Centre de Congrès le Régent pour un moment exceptionnel.',
    'Route Cantonale 43, Crans-Montana, Valais, Suisse',
    46.30505508318389,
    7.475517397943852,
    '2026-07-09',
    '18:30:00',
    '2026-07-09',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-2501',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show à Chamoson',
    'Rendez-vous à Chamoson pour one-man show. Cet événement se tiendra au/à la Salle de Chamoson. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 49, Chamoson, Valais, Suisse',
    46.19618953829899,
    7.221482559690879,
    '2026-07-09',
    '14:00:00',
    '2026-07-09',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-5554',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film à Verbier',
    'Découvrez projection de film au/à la Centre Sportif de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 36, Verbier, Valais, Suisse',
    46.10122389626292,
    7.230149782463252,
    '2026-07-13',
    '10:00:00',
    '2026-07-13',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.verbier.ch/agenda/event-7679',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée au Salle de la Matze',
    'La commune de Sion vous invite à randonnée guidée. Rendez-vous au/à la Salle de la Matze pour un moment exceptionnel.',
    'Rue de l''Église 48, Sion, Valais, Suisse',
    46.22952754498325,
    7.368806830057598,
    '2026-07-15',
    '15:30:00',
    '2026-07-15',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-5781',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Édition 2026',
    'Découvrez marché de printemps au/à la Thermalquellen de Leukerbad. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 39, Leukerbad, Valais, Suisse',
    46.375944700916385,
    7.62256787959076,
    '2026-07-16',
    '09:30:00',
    '2026-07-16',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.leukerbad.ch/agenda/event-1650',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village au Vernissage Hotel',
    'Rendez-vous à Zermatt pour fête de village. Cet événement se tiendra au/à la Vernissage Hotel. Ne manquez pas cette occasion unique!',
    'Route Cantonale 16, Zermatt, Valais, Suisse',
    46.02555034989898,
    7.7509967615733535,
    '2026-07-17',
    '10:00:00',
    '2026-07-17',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2605',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking - Édition 2026',
    'Découvrez networking au/à la Manoir de la Ville de Martigny. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 34, Martigny, Valais, Suisse',
    46.098392058403924,
    7.065545005006729,
    '2026-07-17',
    '20:00:00',
    '2026-07-17',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.martigny.ch/agenda/event-7858',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif à Crans-Montana',
    'Rendez-vous à Crans-Montana pour atelier créatif. Cet événement se tiendra au/à la Golf de Crans. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 4, Crans-Montana, Valais, Suisse',
    46.303091908150556,
    7.480216149381623,
    '2026-07-18',
    '18:30:00',
    '2026-07-18',
    '["Culture > Workshops"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-3045',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Verbier',
    'Découvrez exposition d''art au/à la Centre Sportif de Verbier. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 34, Verbier, Valais, Suisse',
    46.0965478190472,
    7.227639586646107,
    '2026-07-19',
    '20:30:00',
    '2026-07-19',
    '["Culture > Expositions"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5674',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Printemps 2026',
    'Rendez-vous à Verbier pour marché de printemps. Cet événement se tiendra au/à la Église de Verbier. Ne manquez pas cette occasion unique!',
    'Place Centrale 37, Verbier, Valais, Suisse',
    46.10107595415496,
    7.2295313998123545,
    '2026-07-19',
    '08:30:00',
    '2026-07-19',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5591',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show - Anzère',
    'Rendez-vous à Anzère pour one-man show. Cet événement se tiendra au/à la Théâtre de Anzère. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 29, Anzère, Valais, Suisse',
    46.29400840041823,
    7.401150286420906,
    '2026-07-19',
    '15:30:00',
    '2026-07-19',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.anzère.ch/agenda/event-2143',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz - Édition 2026',
    'Rendez-vous à Leytron pour soirée quiz. Cet événement se tiendra au/à la Pub de Leytron. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 19, Leytron, Valais, Suisse',
    46.18729234258255,
    7.202467015064857,
    '2026-07-20',
    '22:00:00',
    '2026-07-20',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.leytron.ch/agenda/event-1270',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz',
    'La commune de Crans-Montana vous invite à soirée quiz. Rendez-vous au/à la Golf de Crans pour un moment exceptionnel.',
    'Avenue de la Gare 29, Crans-Montana, Valais, Suisse',
    46.30594857147049,
    7.476292983056778,
    '2026-07-20',
    '21:00:00',
    '2026-07-20',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-4544',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique - Printemps 2026',
    'Découvrez festival de musique au/à la Casino Crans-Montana de Crans-Montana. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 44, Crans-Montana, Valais, Suisse',
    46.305469014275104,
    7.479928845967123,
    '2026-07-20',
    '22:00:00',
    '2026-07-22',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-3098',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante au Place de Evolène',
    'Découvrez brocante au/à la Place de Evolène de Evolène. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Bourg 33, Evolène, Valais, Suisse',
    46.1157084850363,
    7.488754725605048,
    '2026-07-21',
    '09:00:00',
    '2026-07-21',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.evolène.ch/agenda/event-5036',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art au Salle Communale',
    'Rendez-vous à Zermatt pour exposition d''art. Cet événement se tiendra au/à la Salle Communale. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 38, Zermatt, Valais, Suisse',
    46.02274972049686,
    7.749445230397501,
    '2026-07-22',
    '10:00:00',
    '2026-07-22',
    '["Culture > Expositions"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-8426',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale - Édition 2026',
    'Verbier accueille comédie musicale le 24 July 2026. Venez nombreux au/à la Salle des Combins!',
    'Chemin des Vignes 10, Verbier, Valais, Suisse',
    46.10005267333201,
    7.227426210007682,
    '2026-07-24',
    '19:30:00',
    '2026-07-24',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5219',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village - Ayent',
    'Découvrez fête de village au/à la Place de Ayent de Ayent. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 26, Ayent, Valais, Suisse',
    46.28233329855124,
    7.4162715361222,
    '2026-07-24',
    '15:00:00',
    '2026-07-24',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.ayent.ch/agenda/event-7612',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval - Édition 2026',
    'Zermatt accueille carnaval le 25 July 2026. Venez nombreux au/à la Centre culturel!',
    'Avenue de la Gare 42, Zermatt, Valais, Suisse',
    46.015774507515395,
    7.753069224849979,
    '2026-07-25',
    '20:00:00',
    '2026-07-25',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-5877',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ',
    'Découvrez soirée dj au/à la Salle de Saxon de Saxon. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 36, Saxon, Valais, Suisse',
    46.15251780259001,
    7.166469039376765,
    '2026-07-26',
    '19:30:00',
    '2026-07-26',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.saxon.ch/agenda/event-2514',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Salvan',
    'Atelier créatif organisé(e) au/à la Centre Culturel de Salvan, Salvan. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 27, Salvan, Valais, Suisse',
    46.11177826712116,
    7.020648975054704,
    '2026-07-26',
    '15:00:00',
    '2026-07-26',
    '["Culture > Workshops"]'::jsonb,
    'https://www.salvan.ch/agenda/event-6664',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée',
    'Rendez-vous à Zermatt pour randonnée guidée. Cet événement se tiendra au/à la Centre culturel. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 17, Zermatt, Valais, Suisse',
    46.02329506619162,
    7.752625224922141,
    '2026-07-28',
    '14:00:00',
    '2026-07-28',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-7465',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art au Musée de Ovronnaz',
    'Exposition d''art organisé(e) au/à la Musée de Ovronnaz, Ovronnaz. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 11, Ovronnaz, Valais, Suisse',
    46.1876419901762,
    7.164519040445416,
    '2026-07-28',
    '17:30:00',
    '2026-07-28',
    '["Culture > Expositions"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-7588',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert au La Poste Culture',
    'Visp accueille concert le 29 July 2026. Venez nombreux au/à la La Poste Culture!',
    'Place Centrale 31, Visp, Valais, Suisse',
    46.291543667505266,
    7.882970809951725,
    '2026-07-29',
    '19:30:00',
    '2026-07-29',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-4451',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Chamoson',
    'Rendez-vous à Chamoson pour compétition de ski. Cet événement se tiendra au/à la Piste de Chamoson. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 1, Chamoson, Valais, Suisse',
    46.195408161972765,
    7.212012141807437,
    '2026-08-02',
    '18:00:00',
    '2026-08-02',
    '["Sport > Glisse"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-9766',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Crans-Montana',
    'Crans-Montana accueille compétition de ski le 06 August 2026. Venez nombreux au/à la Golf de Crans!',
    'Rue de l''Église 34, Crans-Montana, Valais, Suisse',
    46.3077724877352,
    7.478907816308599,
    '2026-08-06',
    '19:30:00',
    '2026-08-06',
    '["Sport > Glisse"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-2069',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Course populaire à Zermatt',
    'Zermatt accueille course populaire le 07 August 2026. Venez nombreux au/à la Vernissage Hotel!',
    'Avenue de la Gare 23, Zermatt, Valais, Suisse',
    46.016959675154595,
    7.750152686526694,
    '2026-08-07',
    '14:30:00',
    '2026-08-07',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2237',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto à Crans-Montana',
    'La commune de Crans-Montana vous invite à loto. Rendez-vous au/à la Centre de Congrès le Régent pour un moment exceptionnel.',
    'Rue du Rhône 18, Crans-Montana, Valais, Suisse',
    46.308740230318236,
    7.4767767245954495,
    '2026-08-08',
    '19:30:00',
    '2026-08-08',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-8756',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz au Cave de Ayent',
    'Découvrez concert jazz au/à la Cave de Ayent de Ayent. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 10, Ayent, Valais, Suisse',
    46.28366688158367,
    7.418274609242097,
    '2026-08-09',
    '20:00:00',
    '2026-08-09',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.ayent.ch/agenda/event-4886',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert',
    'La commune de Verbier vous invite à concert. Rendez-vous au/à la W Hotel pour un moment exceptionnel.',
    'Rue du Bourg 38, Verbier, Valais, Suisse',
    46.09827982472614,
    7.228335345274557,
    '2026-08-09',
    '20:00:00',
    '2026-08-09',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.verbier.ch/agenda/event-1621',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto à Ovronnaz',
    'Rendez-vous à Ovronnaz pour loto. Cet événement se tiendra au/à la Salle Polyvalente de Ovronnaz. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 32, Ovronnaz, Valais, Suisse',
    46.1966140764295,
    7.164294827326837,
    '2026-08-09',
    '19:00:00',
    '2026-08-09',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-8811',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Printemps 2026',
    'Marché de printemps organisé(e) au/à la Stockalperschloss, Brig. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 32, Brig, Valais, Suisse',
    46.3153414567879,
    7.982312205243659,
    '2026-08-10',
    '08:00:00',
    '2026-08-10',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.brig.ch/agenda/event-4849',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Printemps 2026',
    'Rendez-vous à Sierre pour marché gourmand. Cet événement se tiendra au/à la Château de Villa. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 21, Sierre, Valais, Suisse',
    46.29589031791138,
    7.536417008775105,
    '2026-08-11',
    '09:00:00',
    '2026-08-11',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.sierre.ch/agenda/event-1548',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brunch musical - Printemps 2026',
    'Découvrez brunch musical au/à la Théâtre de Valère de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 6, Sion, Valais, Suisse',
    46.233157961394255,
    7.368548133435286,
    '2026-08-12',
    '11:30:00',
    '2026-08-12',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.sion.ch/agenda/event-3389',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand au Place de Chamoson',
    'La commune de Chamoson vous invite à marché gourmand. Rendez-vous au/à la Place de Chamoson pour un moment exceptionnel.',
    'Rue du Bourg 2, Chamoson, Valais, Suisse',
    46.20290750888781,
    7.212572012602548,
    '2026-08-13',
    '09:00:00',
    '2026-08-13',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-6155',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Printemps 2026',
    'Découvrez randonnée guidée au/à la Casino de Sion de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 16, Sion, Valais, Suisse',
    46.231123984891966,
    7.363698706654548,
    '2026-08-13',
    '14:00:00',
    '2026-08-13',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-8488',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Édition 2026',
    'Martigny accueille trail le 16 August 2026. Venez nombreux au/à la Fondation Gianadda!',
    'Chemin des Vignes 43, Martigny, Valais, Suisse',
    46.095647045005684,
    7.065008584867482,
    '2026-08-16',
    '14:00:00',
    '2026-08-16',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-9734',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show - Édition 2026',
    'Salvan accueille one-man show le 17 August 2026. Venez nombreux au/à la Salle de Salvan!',
    'Rue de l''Église 37, Salvan, Valais, Suisse',
    46.117473016632346,
    7.012461428711395,
    '2026-08-17',
    '10:00:00',
    '2026-08-17',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.salvan.ch/agenda/event-7796',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert - Édition 2026',
    'Rendez-vous à Evolène pour concert. Cet événement se tiendra au/à la Église de Evolène. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 15, Evolène, Valais, Suisse',
    46.117773939392094,
    7.491160431993892,
    '2026-08-17',
    '20:30:00',
    '2026-08-17',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.evolène.ch/agenda/event-9419',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Printemps 2026',
    'Concert de musique classique organisé(e) au/à la Château de Villa, Sierre. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 16, Sierre, Valais, Suisse',
    46.29018824404386,
    7.53355746613218,
    '2026-08-17',
    '22:30:00',
    '2026-08-17',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.sierre.ch/agenda/event-3254',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique',
    'Rendez-vous à Zermatt pour concert de musique classique. Cet événement se tiendra au/à la Salle Communale. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 1, Zermatt, Valais, Suisse',
    46.02175809033837,
    7.750089180173546,
    '2026-08-18',
    '22:30:00',
    '2026-08-18',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-1698',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage',
    'Rendez-vous à Monthey pour vernissage. Cet événement se tiendra au/à la Salle Communale. Ne manquez pas cette occasion unique!',
    'Route Cantonale 6, Monthey, Valais, Suisse',
    46.24970737857426,
    6.954096564504324,
    '2026-08-20',
    '20:00:00',
    '2026-08-20',
    '["Culture > Expositions"]'::jsonb,
    'https://www.monthey.ch/agenda/event-5293',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval au Salle des Combins',
    'Rendez-vous à Verbier pour carnaval. Cet événement se tiendra au/à la Salle des Combins. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 10, Verbier, Valais, Suisse',
    46.09511611863423,
    7.228004660279383,
    '2026-08-22',
    '19:00:00',
    '2026-08-22',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-5780',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand à Sierre',
    'Marché gourmand organisé(e) au/à la Salle de Borzuat, Sierre. Événement ouvert à tous, petits et grands.',
    'Place Centrale 7, Sierre, Valais, Suisse',
    46.292728865623594,
    7.536357419084041,
    '2026-08-23',
    '08:30:00',
    '2026-08-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.sierre.ch/agenda/event-4409',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique au Théâtre de Valère',
    'Sion accueille concert de musique classique le 23 August 2026. Venez nombreux au/à la Théâtre de Valère!',
    'Chemin des Vignes 27, Sion, Valais, Suisse',
    46.23647145194053,
    7.36578005463485,
    '2026-08-23',
    '20:30:00',
    '2026-08-23',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.sion.ch/agenda/event-1974',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand à Brig',
    'Marché gourmand organisé(e) au/à la Centre Culturel, Brig. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 29, Brig, Valais, Suisse',
    46.321308902878734,
    7.980724228132955,
    '2026-08-23',
    '08:00:00',
    '2026-08-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.brig.ch/agenda/event-3576',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Sion',
    'Sion accueille marché de printemps le 23 August 2026. Venez nombreux au/à la Caves Varone!',
    'Route Cantonale 9, Sion, Valais, Suisse',
    46.23054528255185,
    7.367699226152015,
    '2026-08-23',
    '09:30:00',
    '2026-08-23',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sion.ch/agenda/event-7296',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail au Salle de la Matze',
    'Rendez-vous à Sion pour trail. Cet événement se tiendra au/à la Salle de la Matze. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 47, Sion, Valais, Suisse',
    46.23238529138765,
    7.370245515949653,
    '2026-08-23',
    '10:30:00',
    '2026-08-23',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-2369',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz',
    'Rendez-vous à Zermatt pour concert jazz. Cet événement se tiendra au/à la Centre culturel. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 33, Zermatt, Valais, Suisse',
    46.01654145257653,
    7.7506862830953756,
    '2026-08-24',
    '22:30:00',
    '2026-08-24',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-1613',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski',
    'Compétition de ski organisé(e) au/à la Salle des Combins, Verbier. Événement ouvert à tous, petits et grands.',
    'Place Centrale 30, Verbier, Valais, Suisse',
    46.10010111815278,
    7.229504913124592,
    '2026-08-24',
    '20:00:00',
    '2026-08-24',
    '["Sport > Glisse"]'::jsonb,
    'https://www.verbier.ch/agenda/event-4096',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps à Brig',
    'Marché de printemps organisé(e) au/à la Stockalperschloss, Brig. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 30, Brig, Valais, Suisse',
    46.318077153895246,
    7.985857694137399,
    '2026-08-26',
    '08:00:00',
    '2026-08-26',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.brig.ch/agenda/event-4627',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert à Visp',
    'Visp accueille concert le 27 August 2026. Venez nombreux au/à la Théâtre La Poste!',
    'Rue du Rhône 13, Visp, Valais, Suisse',
    46.29636285390209,
    7.886849589396265,
    '2026-08-27',
    '21:30:00',
    '2026-08-27',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-6340',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage à Verbier',
    'Rendez-vous à Verbier pour vernissage. Cet événement se tiendra au/à la Centre Sportif. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 43, Verbier, Valais, Suisse',
    46.09145973670242,
    7.229824843128918,
    '2026-08-28',
    '15:00:00',
    '2026-08-28',
    '["Culture > Expositions"]'::jsonb,
    'https://www.verbier.ch/agenda/event-9816',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film - Verbier',
    'Rendez-vous à Verbier pour projection de film. Cet événement se tiendra au/à la Église de Verbier. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 22, Verbier, Valais, Suisse',
    46.09490730710181,
    7.232379735740396,
    '2026-08-28',
    '20:30:00',
    '2026-08-28',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.verbier.ch/agenda/event-1916',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps à Martigny',
    'Rendez-vous à Martigny pour marché de printemps. Cet événement se tiendra au/à la Forum Claudel. Ne manquez pas cette occasion unique!',
    'Rue du Bourg 12, Martigny, Valais, Suisse',
    46.10417846861367,
    7.065775285122691,
    '2026-08-28',
    '10:30:00',
    '2026-08-28',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.martigny.ch/agenda/event-1979',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel - Visp',
    'Rendez-vous à Visp pour salon professionnel. Cet événement se tiendra au/à la Théâtre La Poste. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 22, Visp, Valais, Suisse',
    46.2963531908738,
    7.88098677003006,
    '2026-08-29',
    '10:00:00',
    '2026-08-29',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-2787',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz à Zermatt',
    'La commune de Zermatt vous invite à soirée quiz. Rendez-vous au/à la Église de Zermatt pour un moment exceptionnel.',
    'Rue du Bourg 18, Zermatt, Valais, Suisse',
    46.02049523951029,
    7.745915068282596,
    '2026-08-29',
    '21:30:00',
    '2026-08-29',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-6967',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence à Crans-Montana',
    'La commune de Crans-Montana vous invite à conférence. Rendez-vous au/à la Centre de Congrès le Régent pour un moment exceptionnel.',
    'Rue du Rhône 18, Crans-Montana, Valais, Suisse',
    46.31076186169145,
    7.484101910597055,
    '2026-08-29',
    '18:00:00',
    '2026-08-29',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-5765',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking à Sierre',
    'Découvrez networking au/à la Forum Sierre de Sierre. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 36, Sierre, Valais, Suisse',
    46.288893399476045,
    7.529893920025876,
    '2026-08-29',
    '18:00:00',
    '2026-08-29',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.sierre.ch/agenda/event-6045',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique - Printemps 2026',
    'Découvrez concert de musique classique au/à la Théâtre de Evolène de Evolène. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 29, Evolène, Valais, Suisse',
    46.10824383303716,
    7.491417521532179,
    '2026-09-01',
    '19:30:00',
    '2026-09-01',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.evolène.ch/agenda/event-2167',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Printemps 2026',
    'Trail organisé(e) au/à la Place de l''Hôtel de Ville, Monthey. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 30, Monthey, Valais, Suisse',
    46.248579624661204,
    6.953598646404844,
    '2026-09-01',
    '17:30:00',
    '2026-09-01',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.monthey.ch/agenda/event-8074',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique',
    'La commune de Crans-Montana vous invite à festival de musique. Rendez-vous au/à la Casino Crans-Montana pour un moment exceptionnel.',
    'Rue du Bourg 19, Crans-Montana, Valais, Suisse',
    46.31071118882039,
    7.477389795459523,
    '2026-09-05',
    '21:30:00',
    '2026-09-08',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-7366',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey à Anzère',
    'Anzère accueille match de hockey le 05 September 2026. Venez nombreux au/à la Patinoire de Anzère!',
    'Rue de l''Église 13, Anzère, Valais, Suisse',
    46.28736444457287,
    7.400763739417491,
    '2026-09-05',
    '19:30:00',
    '2026-09-05',
    '["Sport > Glisse"]'::jsonb,
    'https://www.anzère.ch/agenda/event-5989',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique - Lens',
    'La commune de Lens vous invite à festival de musique. Rendez-vous au/à la Plein Air de Lens pour un moment exceptionnel.',
    'Chemin des Vignes 26, Lens, Valais, Suisse',
    46.28520466121016,
    7.4337024223845,
    '2026-09-06',
    '22:30:00',
    '2026-09-08',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.lens.ch/agenda/event-7495',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking au Centre sportif Kalbermatten',
    'Découvrez networking au/à la Centre sportif Kalbermatten de Saas-Fee. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 26, Saas-Fee, Valais, Suisse',
    46.10643995377711,
    7.925298059897605,
    '2026-09-06',
    '10:00:00',
    '2026-09-06',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.saasfee.ch/agenda/event-1589',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Sierre',
    'La commune de Sierre vous invite à marché de printemps. Rendez-vous au/à la Salle de Borzuat pour un moment exceptionnel.',
    'Rue du Rhône 17, Sierre, Valais, Suisse',
    46.29378401161799,
    7.538542331451946,
    '2026-09-06',
    '10:30:00',
    '2026-09-06',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sierre.ch/agenda/event-2312',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz',
    'Concert Jazz organisé(e) au/à la Place de la Planta, Sion. Événement ouvert à tous, petits et grands.',
    'Place Centrale 7, Sion, Valais, Suisse',
    46.238091272980895,
    7.362722303981229,
    '2026-09-07',
    '20:30:00',
    '2026-09-07',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.sion.ch/agenda/event-7860',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante',
    'Chamoson accueille brocante le 08 September 2026. Venez nombreux au/à la Place de Chamoson!',
    'Rue du Rhône 4, Chamoson, Valais, Suisse',
    46.20278144692337,
    7.216456129610381,
    '2026-09-08',
    '10:30:00',
    '2026-09-08',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-2959',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence au Église de Zermatt',
    'La commune de Zermatt vous invite à conférence. Rendez-vous au/à la Église de Zermatt pour un moment exceptionnel.',
    'Chemin des Vignes 42, Zermatt, Valais, Suisse',
    46.02369187033934,
    7.744542745358515,
    '2026-09-09',
    '17:30:00',
    '2026-09-09',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-1558',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante au Place de Ayent',
    'La commune de Ayent vous invite à brocante. Rendez-vous au/à la Place de Ayent pour un moment exceptionnel.',
    'Rue du Bourg 39, Ayent, Valais, Suisse',
    46.279003858397076,
    7.416921599717294,
    '2026-09-10',
    '08:30:00',
    '2026-09-10',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.ayent.ch/agenda/event-5316',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Printemps 2026',
    'Découvrez marché gourmand au/à la Église de Zermatt de Zermatt. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 34, Zermatt, Valais, Suisse',
    46.02123465724536,
    7.7516478106808435,
    '2026-09-11',
    '09:30:00',
    '2026-09-11',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-6963',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand au Théâtre du Crochetan',
    'Rendez-vous à Monthey pour marché gourmand. Cet événement se tiendra au/à la Théâtre du Crochetan. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 42, Monthey, Valais, Suisse',
    46.251174410420376,
    6.953541719297589,
    '2026-09-12',
    '10:30:00',
    '2026-09-12',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.monthey.ch/agenda/event-3424',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film - Printemps 2026',
    'Découvrez projection de film au/à la Cinéma de Anzère de Anzère. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 16, Anzère, Valais, Suisse',
    46.286982819123196,
    7.3962686275011835,
    '2026-09-16',
    '10:30:00',
    '2026-09-16',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.anzère.ch/agenda/event-4138',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Zermatt',
    'Découvrez soirée dj au/à la Église de Zermatt de Zermatt. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 43, Zermatt, Valais, Suisse',
    46.01591499794042,
    7.74764088347403,
    '2026-09-18',
    '22:30:00',
    '2026-09-18',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2359',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert à Lens',
    'La commune de Lens vous invite à concert. Rendez-vous au/à la Église de Lens pour un moment exceptionnel.',
    'Rue du Rhône 5, Lens, Valais, Suisse',
    46.28101803992658,
    7.432106989985691,
    '2026-09-19',
    '21:00:00',
    '2026-09-19',
    '["Music > Pop / Vari\u00e9t\u00e9"]'::jsonb,
    'https://www.lens.ch/agenda/event-2123',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village - Édition 2026',
    'Chamoson accueille fête de village le 19 September 2026. Venez nombreux au/à la Place de Chamoson!',
    'Chemin des Vignes 43, Chamoson, Valais, Suisse',
    46.19807114810906,
    7.220895048257506,
    '2026-09-19',
    '20:30:00',
    '2026-09-19',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-7319',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval',
    'La commune de Zermatt vous invite à carnaval. Rendez-vous au/à la Vernissage Hotel pour un moment exceptionnel.',
    'Avenue de la Gare 50, Zermatt, Valais, Suisse',
    46.01596832762613,
    7.750535514242084,
    '2026-09-21',
    '14:00:00',
    '2026-09-21',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-7704',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Édition 2026',
    'Marché gourmand organisé(e) au/à la Place de Riddes, Riddes. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 38, Riddes, Valais, Suisse',
    46.17093299379839,
    7.2356155738772205,
    '2026-09-23',
    '08:30:00',
    '2026-09-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.riddes.ch/agenda/event-8351',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art à Champéry',
    'Rendez-vous à Champéry pour exposition d''art. Cet événement se tiendra au/à la Musée de Champéry. Ne manquez pas cette occasion unique!',
    'Place Centrale 50, Champéry, Valais, Suisse',
    46.170170210582704,
    6.8648044793455085,
    '2026-09-23',
    '20:00:00',
    '2026-09-23',
    '["Culture > Expositions"]'::jsonb,
    'https://www.champéry.ch/agenda/event-2733',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Printemps 2026',
    'Soirée DJ organisé(e) au/à la Club de Saxon, Saxon. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 22, Saxon, Valais, Suisse',
    46.15087051810171,
    7.168964246635651,
    '2026-09-25',
    '22:30:00',
    '2026-09-25',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.saxon.ch/agenda/event-1275',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village à Fully',
    'Fully accueille fête de village le 25 September 2026. Venez nombreux au/à la Place de Fully!',
    'Rue de l''Église 49, Fully, Valais, Suisse',
    46.13630645896794,
    7.120168290856692,
    '2026-09-25',
    '15:00:00',
    '2026-09-25',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.fully.ch/agenda/event-6026',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence - Édition 2026',
    'Rendez-vous à Sierre pour conférence. Cet événement se tiendra au/à la Salle de Borzuat. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 6, Sierre, Valais, Suisse',
    46.28725891436059,
    7.531686413770051,
    '2026-09-26',
    '18:00:00',
    '2026-09-26',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.sierre.ch/agenda/event-6258',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Printemps 2026',
    'Rendez-vous à Fully pour randonnée guidée. Cet événement se tiendra au/à la Départ de Fully. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 50, Fully, Valais, Suisse',
    46.13070069527344,
    7.113550743711086,
    '2026-09-28',
    '17:30:00',
    '2026-09-28',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.fully.ch/agenda/event-8116',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel',
    'Salon professionnel organisé(e) au/à la Salle Communale, Visp. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 38, Visp, Valais, Suisse',
    46.295245284269605,
    7.885616524703423,
    '2026-09-29',
    '19:30:00',
    '2026-09-29',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-1859',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Édition 2026',
    'Découvrez randonnée guidée au/à la Théâtre de Valère de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 50, Sion, Valais, Suisse',
    46.23692437696269,
    7.365805366249239,
    '2026-10-01',
    '19:00:00',
    '2026-10-01',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-3400',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence à Sion',
    'Rendez-vous à Sion pour conférence. Cet événement se tiendra au/à la Médiathèque Valais. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 24, Sion, Valais, Suisse',
    46.230290002980205,
    7.368520832590066,
    '2026-10-01',
    '20:30:00',
    '2026-10-01',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.sion.ch/agenda/event-1921',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin - Sierre',
    'Sierre accueille dégustation de vin le 01 October 2026. Venez nombreux au/à la Forum Sierre!',
    'Route Cantonale 13, Sierre, Valais, Suisse',
    46.29524510642291,
    7.5297295992112865,
    '2026-10-01',
    '18:00:00',
    '2026-10-01',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.sierre.ch/agenda/event-9421',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence - Printemps 2026',
    'Découvrez conférence au/à la Centre sportif Kalbermatten de Saas-Fee. Un moment convivial à partager en famille ou entre amis.',
    'Rue de l''Église 28, Saas-Fee, Valais, Suisse',
    46.10807514699053,
    7.923125665936554,
    '2026-10-02',
    '18:30:00',
    '2026-10-02',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.saasfee.ch/agenda/event-5017',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif',
    'La commune de Sion vous invite à atelier créatif. Rendez-vous au/à la Salle de la Matze pour un moment exceptionnel.',
    'Rue de l''Église 38, Sion, Valais, Suisse',
    46.228688942731026,
    7.365565779608724,
    '2026-10-02',
    '14:30:00',
    '2026-10-02',
    '["Culture > Workshops"]'::jsonb,
    'https://www.sion.ch/agenda/event-3124',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif au Église de Zermatt',
    'La commune de Zermatt vous invite à atelier créatif. Rendez-vous au/à la Église de Zermatt pour un moment exceptionnel.',
    'Route Cantonale 35, Zermatt, Valais, Suisse',
    46.02131652309018,
    7.750352783673023,
    '2026-10-03',
    '19:00:00',
    '2026-10-03',
    '["Culture > Workshops"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-2966',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert de musique classique au Salle Communale',
    'Zermatt accueille concert de musique classique le 04 October 2026. Venez nombreux au/à la Salle Communale!',
    'Rue du Rhône 49, Zermatt, Valais, Suisse',
    46.021911992394585,
    7.750957840378395,
    '2026-10-04',
    '19:30:00',
    '2026-10-04',
    '["Music > Classique > Formes"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-1751',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Édition 2026',
    'La commune de Ayent vous invite à marché gourmand. Rendez-vous au/à la Place de Ayent pour un moment exceptionnel.',
    'Rue du Bourg 13, Ayent, Valais, Suisse',
    46.28303475711079,
    7.417999698498063,
    '2026-10-04',
    '08:00:00',
    '2026-10-04',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.ayent.ch/agenda/event-5751',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village à Brig',
    'La commune de Brig vous invite à fête de village. Rendez-vous au/à la Stockalperschloss pour un moment exceptionnel.',
    'Rue du Bourg 48, Brig, Valais, Suisse',
    46.31324515933087,
    7.985694487357175,
    '2026-10-09',
    '15:30:00',
    '2026-10-09',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.brig.ch/agenda/event-9853',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking - Printemps 2026',
    'Rendez-vous à Vétroz pour networking. Cet événement se tiendra au/à la Restaurant de Vétroz. Ne manquez pas cette occasion unique!',
    'Route Cantonale 43, Vétroz, Valais, Suisse',
    46.212534298087775,
    7.2848406854073104,
    '2026-10-10',
    '18:30:00',
    '2026-10-10',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.vétroz.ch/agenda/event-8572',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Fête de village - Édition 2026',
    'Chamoson accueille fête de village le 11 October 2026. Venez nombreux au/à la Village de Chamoson!',
    'Route Cantonale 13, Chamoson, Valais, Suisse',
    46.20422746795743,
    7.220345719161116,
    '2026-10-11',
    '10:30:00',
    '2026-10-11',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.chamoson.ch/agenda/event-7981',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art - Édition 2026',
    'Monthey accueille exposition d''art le 14 October 2026. Venez nombreux au/à la Château de Monthey!',
    'Rue du Bourg 11, Monthey, Valais, Suisse',
    46.25010478728891,
    6.949247268990349,
    '2026-10-14',
    '10:30:00',
    '2026-10-14',
    '["Culture > Expositions"]'::jsonb,
    'https://www.monthey.ch/agenda/event-1094',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Printemps 2026',
    'La commune de Zermatt vous invite à trail. Rendez-vous au/à la Salle Communale pour un moment exceptionnel.',
    'Rue du Bourg 50, Zermatt, Valais, Suisse',
    46.020632348232176,
    7.745872747502302,
    '2026-10-16',
    '15:00:00',
    '2026-10-16',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4092',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel - Édition 2026',
    'La commune de Visp vous invite à salon professionnel. Rendez-vous au/à la Théâtre La Poste pour un moment exceptionnel.',
    'Rue du Bourg 16, Visp, Valais, Suisse',
    46.29114341332984,
    7.886269796064275,
    '2026-10-17',
    '20:30:00',
    '2026-10-17',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.visp.ch/agenda/event-9595',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval - Printemps 2026',
    'Rendez-vous à Martigny pour carnaval. Cet événement se tiendra au/à la Fondation Gianadda. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 16, Martigny, Valais, Suisse',
    46.0963585698072,
    7.06210680209915,
    '2026-10-19',
    '18:00:00',
    '2026-10-19',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.martigny.ch/agenda/event-9102',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval - Printemps 2026',
    'Carnaval organisé(e) au/à la Golf de Crans, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 11, Crans-Montana, Valais, Suisse',
    46.30883961391965,
    7.481317582355995,
    '2026-10-22',
    '14:00:00',
    '2026-10-22',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-4443',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin - Brig',
    'Dégustation de vin organisé(e) au/à la Simplonhalle, Brig. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 47, Brig, Valais, Suisse',
    46.31367847180485,
    7.9845013465333805,
    '2026-10-23',
    '15:00:00',
    '2026-10-23',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.brig.ch/agenda/event-2728',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Printemps 2026',
    'Sion accueille randonnée guidée le 23 October 2026. Venez nombreux au/à la Médiathèque Valais!',
    'Rue du Rhône 36, Sion, Valais, Suisse',
    46.22989889455004,
    7.3648123498220475,
    '2026-10-23',
    '20:00:00',
    '2026-10-23',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-4016',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Printemps 2026',
    'Rendez-vous à Leytron pour compétition de ski. Cet événement se tiendra au/à la Station de Leytron. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 44, Leytron, Valais, Suisse',
    46.18368400941157,
    7.203615278869858,
    '2026-10-23',
    '19:00:00',
    '2026-10-23',
    '["Sport > Glisse"]'::jsonb,
    'https://www.leytron.ch/agenda/event-9309',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey à Sierre',
    'Match de hockey organisé(e) au/à la Salle de Borzuat, Sierre. Événement ouvert à tous, petits et grands.',
    'Avenue de la Gare 22, Sierre, Valais, Suisse',
    46.295869000188674,
    7.530083454172726,
    '2026-10-23',
    '18:00:00',
    '2026-10-23',
    '["Sport > Glisse"]'::jsonb,
    'https://www.sierre.ch/agenda/event-7614',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Course populaire à Zermatt',
    'Zermatt accueille course populaire le 24 October 2026. Venez nombreux au/à la Salle Communale!',
    'Rue du Rhône 33, Zermatt, Valais, Suisse',
    46.02090097745478,
    7.75343387936922,
    '2026-10-24',
    '17:00:00',
    '2026-10-24',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-9010',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film - Printemps 2026',
    'Découvrez projection de film au/à la Stockalperschloss de Brig. Un moment convivial à partager en famille ou entre amis.',
    'Route Cantonale 45, Brig, Valais, Suisse',
    46.31704465006416,
    7.986487993923317,
    '2026-10-25',
    '10:00:00',
    '2026-10-25',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.brig.ch/agenda/event-6258',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Édition 2026',
    'Rendez-vous à Conthey pour soirée dj. Cet événement se tiendra au/à la Salle de Conthey. Ne manquez pas cette occasion unique!',
    'Rue de l''Église 44, Conthey, Valais, Suisse',
    46.220034266955636,
    7.301485034673679,
    '2026-10-26',
    '19:30:00',
    '2026-10-26',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.conthey.ch/agenda/event-7452',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale au Théâtre de Riddes',
    'Comédie musicale organisé(e) au/à la Théâtre de Riddes, Riddes. Événement ouvert à tous, petits et grands.',
    'Place Centrale 37, Riddes, Valais, Suisse',
    46.168932036914306,
    7.2326395701461434,
    '2026-10-26',
    '15:00:00',
    '2026-10-26',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.riddes.ch/agenda/event-7741',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage au W Hotel',
    'Vernissage organisé(e) au/à la W Hotel, Verbier. Événement ouvert à tous, petits et grands.',
    'Place Centrale 7, Verbier, Valais, Suisse',
    46.099570120056796,
    7.227882571654955,
    '2026-10-26',
    '19:30:00',
    '2026-10-26',
    '["Culture > Expositions"]'::jsonb,
    'https://www.verbier.ch/agenda/event-7212',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto',
    'Loto organisé(e) au/à la Régent Palace, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 9, Crans-Montana, Valais, Suisse',
    46.30828959510705,
    7.483349525623154,
    '2026-10-29',
    '18:00:00',
    '2026-10-29',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-8868',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante au Salle de Borzuat',
    'Brocante organisé(e) au/à la Salle de Borzuat, Sierre. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 5, Sierre, Valais, Suisse',
    46.28937987406165,
    7.533928243936601,
    '2026-10-31',
    '09:30:00',
    '2026-10-31',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sierre.ch/agenda/event-2106',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin - Sion',
    'Sion accueille dégustation de vin le 31 October 2026. Venez nombreux au/à la Salle de la Matze!',
    'Rue de l''Église 18, Sion, Valais, Suisse',
    46.23426002592877,
    7.36315454017196,
    '2026-10-31',
    '15:30:00',
    '2026-10-31',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.sion.ch/agenda/event-6405',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski au Château de Tourbillon',
    'Rendez-vous à Sion pour compétition de ski. Cet événement se tiendra au/à la Château de Tourbillon. Ne manquez pas cette occasion unique!',
    'Place Centrale 25, Sion, Valais, Suisse',
    46.23228006951056,
    7.3622169256699355,
    '2026-10-31',
    '20:00:00',
    '2026-10-31',
    '["Sport > Glisse"]'::jsonb,
    'https://www.sion.ch/agenda/event-7525',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz - Édition 2026',
    'Soirée quiz organisé(e) au/à la Fondation Gianadda, Martigny. Événement ouvert à tous, petits et grands.',
    'Rue du Bourg 41, Martigny, Valais, Suisse',
    46.10473996109671,
    7.06174935517531,
    '2026-11-01',
    '22:00:00',
    '2026-11-01',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.martigny.ch/agenda/event-5884',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique - Édition 2026',
    'Découvrez festival de musique au/à la Place de Saxon de Saxon. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Bourg 7, Saxon, Valais, Suisse',
    46.147682496395426,
    7.165174698160748,
    '2026-11-04',
    '19:30:00',
    '2026-11-06',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.saxon.ch/agenda/event-7928',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Course populaire - Printemps 2026',
    'Course populaire organisé(e) au/à la Centre Sportif, Verbier. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 29, Verbier, Valais, Suisse',
    46.100139638240975,
    7.223671720651928,
    '2026-11-05',
    '14:30:00',
    '2026-11-05',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-7684',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale au Thermalquellen',
    'Rendez-vous à Leukerbad pour comédie musicale. Cet événement se tiendra au/à la Thermalquellen. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 24, Leukerbad, Valais, Suisse',
    46.38231708404271,
    7.624747205208488,
    '2026-11-07',
    '14:30:00',
    '2026-11-07',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.leukerbad.ch/agenda/event-6629',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Projection de film',
    'Découvrez projection de film au/à la Salle de Ayent de Ayent. Un moment convivial à partager en famille ou entre amis.',
    'Rue du Rhône 7, Ayent, Valais, Suisse',
    46.27860888195338,
    7.41879687535288,
    '2026-11-09',
    '18:30:00',
    '2026-11-09',
    '["Culture > Cin\u00e9ma & Projections"]'::jsonb,
    'https://www.ayent.ch/agenda/event-9897',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Saint-Maurice',
    'Soirée DJ organisé(e) au/à la Club de Saint-Maurice, Saint-Maurice. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 28, Saint-Maurice, Valais, Suisse',
    46.21246276514882,
    6.995585954487372,
    '2026-11-10',
    '22:00:00',
    '2026-11-10',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.saintmaurice.ch/agenda/event-4184',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ au La Poste Culture',
    'La commune de Visp vous invite à soirée dj. Rendez-vous au/à la La Poste Culture pour un moment exceptionnel.',
    'Place Centrale 12, Visp, Valais, Suisse',
    46.29541107189385,
    7.8840490872334765,
    '2026-11-11',
    '21:00:00',
    '2026-11-11',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.visp.ch/agenda/event-5887',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Conférence à Sion',
    'Rendez-vous à Sion pour conférence. Cet événement se tiendra au/à la Caves Varone. Ne manquez pas cette occasion unique!',
    'Route Cantonale 22, Sion, Valais, Suisse',
    46.232117275010815,
    7.365955353075886,
    '2026-11-11',
    '19:30:00',
    '2026-11-11',
    '["Culture > Conf\u00e9rences & Rencontres"]'::jsonb,
    'https://www.sion.ch/agenda/event-4599',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ à Ovronnaz',
    'Rendez-vous à Ovronnaz pour soirée dj. Cet événement se tiendra au/à la Bar de Ovronnaz. Ne manquez pas cette occasion unique!',
    'Place Centrale 40, Ovronnaz, Valais, Suisse',
    46.191452674188746,
    7.164386188581683,
    '2026-11-11',
    '22:00:00',
    '2026-11-11',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-2696',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante - Édition 2026',
    'La commune de Zermatt vous invite à brocante. Rendez-vous au/à la Vernissage Hotel pour un moment exceptionnel.',
    'Rue de l''Église 28, Zermatt, Valais, Suisse',
    46.01571034611976,
    7.753272236164364,
    '2026-11-14',
    '09:30:00',
    '2026-11-14',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4661',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Édition 2026',
    'La commune de Visp vous invite à soirée dj. Rendez-vous au/à la Théâtre La Poste pour un moment exceptionnel.',
    'Route Cantonale 28, Visp, Valais, Suisse',
    46.28984393234413,
    7.887617388123869,
    '2026-11-15',
    '21:00:00',
    '2026-11-15',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.visp.ch/agenda/event-1219',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Édition 2026',
    'Verbier accueille soirée dj le 17 November 2026. Venez nombreux au/à la Église de Verbier!',
    'Rue du Bourg 2, Verbier, Valais, Suisse',
    46.09157156724523,
    7.230801787178595,
    '2026-11-17',
    '22:30:00',
    '2026-11-17',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.verbier.ch/agenda/event-6512',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski au Station de Lens',
    'La commune de Lens vous invite à compétition de ski. Rendez-vous au/à la Station de Lens pour un moment exceptionnel.',
    'Chemin des Vignes 49, Lens, Valais, Suisse',
    46.281040850387726,
    7.431855791951482,
    '2026-11-18',
    '14:00:00',
    '2026-11-18',
    '["Sport > Glisse"]'::jsonb,
    'https://www.lens.ch/agenda/event-6924',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché de printemps - Anzère',
    'Marché de printemps organisé(e) au/à la Place de Anzère, Anzère. Événement ouvert à tous, petits et grands.',
    'Place Centrale 49, Anzère, Valais, Suisse',
    46.287170771978516,
    7.401398964876319,
    '2026-11-18',
    '10:00:00',
    '2026-11-18',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.anzère.ch/agenda/event-3320',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique - Sion',
    'Sion accueille festival de musique le 18 November 2026. Venez nombreux au/à la Médiathèque Valais!',
    'Place Centrale 3, Sion, Valais, Suisse',
    46.23503721834659,
    7.363359317353465,
    '2026-11-18',
    '20:30:00',
    '2026-11-19',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.sion.ch/agenda/event-5062',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Concert Jazz à Monthey',
    'Monthey accueille concert jazz le 21 November 2026. Venez nombreux au/à la Château de Monthey!',
    'Place Centrale 8, Monthey, Valais, Suisse',
    46.254790953486406,
    6.953317204406956,
    '2026-11-21',
    '19:30:00',
    '2026-11-21',
    '["Music > Jazz / Soul / Funk"]'::jsonb,
    'https://www.monthey.ch/agenda/event-5713',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Édition 2026',
    'Rendez-vous à Verbier pour spectacle de théâtre. Cet événement se tiendra au/à la Centre Sportif. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 8, Verbier, Valais, Suisse',
    46.09154312955016,
    7.233019091081357,
    '2026-11-22',
    '10:00:00',
    '2026-11-22',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-7915',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin - Édition 2026',
    'La commune de Sion vous invite à dégustation de vin. Rendez-vous au/à la Casino de Sion pour un moment exceptionnel.',
    'Chemin des Vignes 28, Sion, Valais, Suisse',
    46.23636056052448,
    7.3707744474389685,
    '2026-11-23',
    '15:00:00',
    '2026-11-23',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.sion.ch/agenda/event-2542',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Salon professionnel',
    'Monthey accueille salon professionnel le 26 November 2026. Venez nombreux au/à la Château de Monthey!',
    'Route Cantonale 15, Monthey, Valais, Suisse',
    46.24608079958261,
    6.948021089907027,
    '2026-11-26',
    '15:00:00',
    '2026-11-26',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.monthey.ch/agenda/event-3831',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Course populaire - Printemps 2026',
    'Rendez-vous à Fully pour course populaire. Cet événement se tiendra au/à la Centre Sportif de Fully. Ne manquez pas cette occasion unique!',
    'Route Cantonale 1, Fully, Valais, Suisse',
    46.13348046561036,
    7.121068278650711,
    '2026-11-27',
    '14:30:00',
    '2026-11-27',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.fully.ch/agenda/event-6974',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante',
    'Sierre accueille brocante le 27 November 2026. Venez nombreux au/à la Château de Villa!',
    'Rue de l''Église 35, Sierre, Valais, Suisse',
    46.288585499066336,
    7.5344457012536115,
    '2026-11-27',
    '10:00:00',
    '2026-11-27',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.sierre.ch/agenda/event-8647',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Brocante - Édition 2026',
    'Brocante organisé(e) au/à la Centre Sportif, Verbier. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 33, Verbier, Valais, Suisse',
    46.09187405004391,
    7.2272063887026885,
    '2026-11-28',
    '10:30:00',
    '2026-11-28',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-7826',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Exposition d''art à Verbier',
    'La commune de Verbier vous invite à exposition d''art. Rendez-vous au/à la Salle des Combins pour un moment exceptionnel.',
    'Rue du Bourg 21, Verbier, Valais, Suisse',
    46.10042434029743,
    7.2305455436632435,
    '2026-11-30',
    '10:00:00',
    '2026-11-30',
    '["Culture > Expositions"]'::jsonb,
    'https://www.verbier.ch/agenda/event-3668',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Fully',
    'Fully accueille atelier créatif le 01 December 2026. Venez nombreux au/à la Atelier de Fully!',
    'Avenue de la Gare 33, Fully, Valais, Suisse',
    46.134592691623055,
    7.114447440795074,
    '2026-12-01',
    '19:00:00',
    '2026-12-01',
    '["Culture > Workshops"]'::jsonb,
    'https://www.fully.ch/agenda/event-9439',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre - Printemps 2026',
    'Martigny accueille spectacle de théâtre le 02 December 2026. Venez nombreux au/à la Fondation Gianadda!',
    'Chemin des Vignes 36, Martigny, Valais, Suisse',
    46.098682805681555,
    7.067100241143315,
    '2026-12-02',
    '10:00:00',
    '2026-12-02',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-3860',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Networking',
    'Rendez-vous à Zermatt pour networking. Cet événement se tiendra au/à la Centre culturel. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 18, Zermatt, Valais, Suisse',
    46.01680841328908,
    7.752585732103077,
    '2026-12-02',
    '18:00:00',
    '2026-12-02',
    '["Business & Communaut\u00e9"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4812',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail - Nendaz',
    'Trail organisé(e) au/à la Centre sportif, Nendaz. Événement ouvert à tous, petits et grands.',
    'Chemin des Vignes 34, Nendaz, Valais, Suisse',
    46.18023645814506,
    7.296291970494891,
    '2026-12-09',
    '20:30:00',
    '2026-12-09',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-2073',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Festival de musique au Église de Zermatt',
    'Zermatt accueille festival de musique le 09 December 2026. Venez nombreux au/à la Église de Zermatt!',
    'Chemin des Vignes 1, Zermatt, Valais, Suisse',
    46.021459423213145,
    7.749201032817285,
    '2026-12-09',
    '22:30:00',
    '2026-12-10',
    '["Festivals & Grandes F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-9315',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée - Sierre',
    'Randonnée guidée organisé(e) au/à la Caves du Paradis, Sierre. Événement ouvert à tous, petits et grands.',
    'Rue du Rhône 25, Sierre, Valais, Suisse',
    46.290219987039244,
    7.53301115569396,
    '2026-12-10',
    '10:30:00',
    '2026-12-10',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sierre.ch/agenda/event-9088',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif - Printemps 2026',
    'La commune de Brig vous invite à atelier créatif. Rendez-vous au/à la Centre Culturel pour un moment exceptionnel.',
    'Route Cantonale 29, Brig, Valais, Suisse',
    46.312283357396666,
    7.979026992268681,
    '2026-12-12',
    '19:30:00',
    '2026-12-12',
    '["Culture > Workshops"]'::jsonb,
    'https://www.brig.ch/agenda/event-2056',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Comédie musicale à Sion',
    'Découvrez comédie musicale au/à la Casino de Sion de Sion. Un moment convivial à partager en famille ou entre amis.',
    'Place Centrale 49, Sion, Valais, Suisse',
    46.22989615321656,
    7.368553171232012,
    '2026-12-15',
    '15:00:00',
    '2026-12-15',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.sion.ch/agenda/event-4845',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Édition 2026',
    'Compétition de ski organisé(e) au/à la Golf de Crans, Crans-Montana. Événement ouvert à tous, petits et grands.',
    'Place Centrale 47, Crans-Montana, Valais, Suisse',
    46.30687737670179,
    7.4839273544404845,
    '2026-12-15',
    '15:30:00',
    '2026-12-15',
    '["Sport > Glisse"]'::jsonb,
    'https://www.cransmontana.ch/agenda/event-5726',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Dégustation de vin',
    'Découvrez dégustation de vin au/à la Domaine Viticole de Vétroz de Vétroz. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 29, Vétroz, Valais, Suisse',
    46.21312258359331,
    7.279612760985749,
    '2026-12-18',
    '19:00:00',
    '2026-12-18',
    '["Food & Drinks > D\u00e9gustations"]'::jsonb,
    'https://www.vétroz.ch/agenda/event-1165',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto à Nendaz',
    'Découvrez loto au/à la Salle polyvalente de Nendaz. Un moment convivial à partager en famille ou entre amis.',
    'Avenue de la Gare 45, Nendaz, Valais, Suisse',
    46.18742334889249,
    7.300872930095575,
    '2026-12-19',
    '18:00:00',
    '2026-12-19',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.nendaz.ch/agenda/event-4260',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval - Édition 2026',
    'Zermatt accueille carnaval le 19 December 2026. Venez nombreux au/à la Vernissage Hotel!',
    'Avenue de la Gare 44, Zermatt, Valais, Suisse',
    46.02175267968912,
    7.750013174962123,
    '2026-12-19',
    '20:00:00',
    '2026-12-19',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-5397',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Match de hockey - Salvan',
    'La commune de Salvan vous invite à match de hockey. Rendez-vous au/à la Aréna de Salvan pour un moment exceptionnel.',
    'Place Centrale 13, Salvan, Valais, Suisse',
    46.118581879580724,
    7.018204212858508,
    '2026-12-20',
    '19:00:00',
    '2026-12-20',
    '["Sport > Glisse"]'::jsonb,
    'https://www.salvan.ch/agenda/event-6967',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail au Médiathèque Valais',
    'Rendez-vous à Sion pour trail. Cet événement se tiendra au/à la Médiathèque Valais. Ne manquez pas cette occasion unique!',
    'Chemin des Vignes 20, Sion, Valais, Suisse',
    46.233791838549465,
    7.3647608310530615,
    '2026-12-20',
    '10:30:00',
    '2026-12-20',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.sion.ch/agenda/event-5577',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée quiz - Édition 2026',
    'Soirée quiz organisé(e) au/à la Simplonhalle, Brig. Événement ouvert à tous, petits et grands.',
    'Place Centrale 42, Brig, Valais, Suisse',
    46.3131538872932,
    7.983347227417512,
    '2026-12-21',
    '22:30:00',
    '2026-12-21',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.brig.ch/agenda/event-3407',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail à Martigny',
    'Martigny accueille trail le 21 December 2026. Venez nombreux au/à la Caves Orsat!',
    'Rue du Rhône 45, Martigny, Valais, Suisse',
    46.101358725400445,
    7.070698463338067,
    '2026-12-21',
    '20:30:00',
    '2026-12-21',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.martigny.ch/agenda/event-7604',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Compétition de ski - Printemps 2026',
    'Rendez-vous à Sierre pour compétition de ski. Cet événement se tiendra au/à la Salle de Borzuat. Ne manquez pas cette occasion unique!',
    'Avenue de la Gare 47, Sierre, Valais, Suisse',
    46.29592451944399,
    7.533960815175357,
    '2026-12-22',
    '14:30:00',
    '2026-12-22',
    '["Sport > Glisse"]'::jsonb,
    'https://www.sierre.ch/agenda/event-8602',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Marché gourmand - Édition 2026',
    'Rendez-vous à Champéry pour marché gourmand. Cet événement se tiendra au/à la Marché de Champéry. Ne manquez pas cette occasion unique!',
    'Rue du Rhône 2, Champéry, Valais, Suisse',
    46.17559286153273,
    6.866459708780531,
    '2026-12-23',
    '08:30:00',
    '2026-12-23',
    '["Food & Drinks > Restauration"]'::jsonb,
    'https://www.champéry.ch/agenda/event-9477',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Loto',
    'Découvrez loto au/à la Stockalperschloss de Brig. Un moment convivial à partager en famille ou entre amis.',
    'Chemin des Vignes 20, Brig, Valais, Suisse',
    46.315200306830015,
    7.986590024166609,
    '2026-12-23',
    '20:30:00',
    '2026-12-23',
    '["Loisirs & Animation > Jeux & Soir\u00e9es"]'::jsonb,
    'https://www.brig.ch/agenda/event-9837',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Trail au Départ de Savièse',
    'Trail organisé(e) au/à la Départ de Savièse, Savièse. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 15, Savièse, Valais, Suisse',
    46.24572023270151,
    7.346099731003913,
    '2026-12-24',
    '18:30:00',
    '2026-12-24',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.savièse.ch/agenda/event-4852',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Atelier créatif',
    'Atelier créatif organisé(e) au/à la Église de Zermatt, Zermatt. Événement ouvert à tous, petits et grands.',
    'Rue de l''Église 48, Zermatt, Valais, Suisse',
    46.01860425532447,
    7.747517990694957,
    '2026-12-24',
    '15:30:00',
    '2026-12-24',
    '["Culture > Workshops"]'::jsonb,
    'https://www.zermatt.ch/agenda/event-4180',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Carnaval',
    'Verbier accueille carnaval le 26 December 2026. Venez nombreux au/à la Église de Verbier!',
    'Chemin des Vignes 41, Verbier, Valais, Suisse',
    46.10102693976011,
    7.227583783525252,
    '2026-12-26',
    '14:00:00',
    '2026-12-26',
    '["Loisirs & Animation > D\u00e9fil\u00e9s & F\u00eates"]'::jsonb,
    'https://www.verbier.ch/agenda/event-8973',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'One-man show',
    'One-man show organisé(e) au/à la Salle de Ovronnaz, Ovronnaz. Événement ouvert à tous, petits et grands.',
    'Route Cantonale 45, Ovronnaz, Valais, Suisse',
    46.188912760159866,
    7.1690842767855365,
    '2026-12-26',
    '19:00:00',
    '2026-12-26',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.ovronnaz.ch/agenda/event-3652',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Spectacle de théâtre',
    'La commune de Verbier vous invite à spectacle de théâtre. Rendez-vous au/à la Centre Sportif pour un moment exceptionnel.',
    'Rue du Rhône 28, Verbier, Valais, Suisse',
    46.09660173147746,
    7.228217331546958,
    '2026-12-29',
    '15:00:00',
    '2026-12-29',
    '["Arts Vivants > Th\u00e9\u00e2tre"]'::jsonb,
    'https://www.verbier.ch/agenda/event-8984',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Soirée DJ - Printemps 2026',
    'La commune de Monthey vous invite à soirée dj. Rendez-vous au/à la Théâtre du Crochetan pour un moment exceptionnel.',
    'Route Cantonale 34, Monthey, Valais, Suisse',
    46.251415214396744,
    6.947930209579756,
    '2026-12-29',
    '19:00:00',
    '2026-12-29',
    '["Music > Electronic > House"]'::jsonb,
    'https://www.monthey.ch/agenda/event-4233',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Randonnée guidée',
    'Salvan accueille randonnée guidée le 30 December 2026. Venez nombreux au/à la Office Du Tourisme de Salvan!',
    'Place Centrale 5, Salvan, Valais, Suisse',
    46.11742037422512,
    7.012545947833599,
    '2026-12-30',
    '19:00:00',
    '2026-12-30',
    '["Sport > Terrestre"]'::jsonb,
    'https://www.salvan.ch/agenda/event-2419',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    'Vernissage au Château de Tourbillon',
    'La commune de Sion vous invite à vernissage. Rendez-vous au/à la Château de Tourbillon pour un moment exceptionnel.',
    'Place Centrale 28, Sion, Valais, Suisse',
    46.23559323696632,
    7.365692100300939,
    '2026-12-31',
    '20:30:00',
    '2026-12-31',
    '["Culture > Expositions"]'::jsonb,
    'https://www.sion.ch/agenda/event-5740',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;
