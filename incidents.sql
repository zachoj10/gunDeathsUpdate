
DROP TABLE incidents;

CREATE TABLE incidents(
	date date,
	state varchar(255),
	city varchar(255),
	address varchar(255),
	killed int,
	injured int, 
	incidentURL varchar(510),
	PRIMARY KEY (incidentURL)
	);