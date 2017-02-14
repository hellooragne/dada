CREATE TABLE `tasks` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `license` varchar(20) NOT NULL DEFAULT '',
  `content` varchar(200) NOT NULL DEFAULT '',
  `voice` varchar(1000) NOT NULL DEFAULT '' COMMENT '语音信息，有可能识别不准确',
  `datetime` datetime NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `community_id` int(10) unsigned NOT NULL,
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '0未确认／5确认／10完成',
  PRIMARY KEY (`id`),
  KEY `datetime` (`datetime`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;