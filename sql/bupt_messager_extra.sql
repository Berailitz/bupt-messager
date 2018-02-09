
--
-- Indexes for dumped tables
--

--
-- Indexes for table `attachment`
--
ALTER TABLE `attachment`
  ADD PRIMARY KEY (`id`),
  ADD KEY `notice` (`notice_id`);

--
-- Indexes for table `chat`
--
ALTER TABLE `chat`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`time`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attachment`
--
ALTER TABLE `attachment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=89;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `attachment`
--
ALTER TABLE `attachment`
  ADD CONSTRAINT `notice` FOREIGN KEY (`notice_id`) REFERENCES `notification` (`id`) ON UPDATE CASCADE;
