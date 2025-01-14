CREATE TABLE IF NOT EXISTS `board_members` (
    `board_id`    INT,
    `user_email`  VARCHAR(100),
    `joined_at`   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`board_id`, `user_email`),
    FOREIGN KEY (`board_id`) REFERENCES `boards`(`board_id`),
    FOREIGN KEY (`user_email`) REFERENCES `users`(`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;