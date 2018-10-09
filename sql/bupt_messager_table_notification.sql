
-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `id` varchar(36) NOT NULL,
  `text` text NOT NULL,
  `title` varchar(80) NOT NULL,
  `url` text NOT NULL,
  `summary` text NOT NULL,
  `date` date NOT NULL,
  `is_pushed` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
