CREATE TABLE `managers` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `community_id` int(11) NOT NULL,
  `level` tinyint(4) unsigned NOT NULL COMMENT '100总管理员／50小区管理员／0小区工作人员',
  `invitation_deadline` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;