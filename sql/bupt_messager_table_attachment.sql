
-- --------------------------------------------------------

--
-- Table structure for table `attachment`
--

CREATE TABLE `attachment` (
  `id` int(11) NOT NULL,
  `notice_id` varchar(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `url` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
