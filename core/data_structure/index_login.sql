CREATE TABLE `index_login` (
  `login` varchar(255) NOT NULL,
  `entity_id` char(32) NOT NULL,
  `search` varchar(255) NOT NULL DEFAULT '',
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`),
  KEY `entity_id` (`entity_id`),
  KEY `search` (`search`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
