CREATE TABLE IF NOT EXISTS `boards` (
    `board_id`    INT           NOT NULL AUTO_INCREMENT,
    `name`        VARCHAR(255)  NOT NULL,
    `created_at`  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    `created_by`  VARCHAR(100)  NOT NULL,
    PRIMARY KEY (`board_id`),
    FOREIGN KEY (`created_by`) REFERENCES `users`(`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;