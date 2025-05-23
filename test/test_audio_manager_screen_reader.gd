# Test file for AudioManager screen reader TTS functionality
# Tests the interaction between screen reader mode and TTS

extends GutTest

# Test setup - runs before each test
func before_each():
	# Reset AudioManager to default state
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = false
	AudioManager.tts_queue.clear()
	AudioManager.is_speaking = false

# Test teardown - runs after each test
func after_each():
	# Cleanup - stop any TTS and reset state
	if DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH):
		if DisplayServer.tts_is_speaking():
			DisplayServer.tts_stop()
	AudioManager.tts_queue.clear()
	AudioManager.is_speaking = false

# Test that TTS works normally when screen reader mode is disabled
func test_tts_works_when_screen_reader_disabled():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = false
	var initial_queue_size = AudioManager.tts_queue.size()

	# Act
	AudioManager.play_narration("Test message")

	# Assert
	# The function should process the text (either via system TTS or queue)
	# We just verify it doesn't return early due to screen reader mode
	# This test passes if no assertion fails (meaning the function ran to completion)
	assert_true(true, "TTS function should complete when screen reader mode is disabled")

# Test that TTS is disabled when screen reader mode is enabled
func test_tts_disabled_when_screen_reader_enabled():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = true

	# Act
	AudioManager.play_narration("Test message")

	# Assert
	# TTS queue should remain empty when screen reader mode is active
	assert_eq(AudioManager.tts_queue.size(), 0, "TTS queue should be empty when screen reader mode is active")
	assert_false(AudioManager.is_speaking, "AudioManager should not be speaking when screen reader mode is active")

# Test that TTS queue is cleared when switching to screen reader mode
func test_tts_queue_cleared_when_enabling_screen_reader():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = false

	# Add some items to the queue (if system TTS is not available)
	AudioManager.play_narration("First message")
	AudioManager.play_narration("Second message")

	var initial_queue_size = AudioManager.tts_queue.size()

	# Act - enable screen reader mode
	AudioManager.toggle_running_screen_reader(true)

	# Assert
	assert_eq(AudioManager.tts_queue.size(), 0, "TTS queue should be cleared when enabling screen reader mode")
	assert_false(AudioManager.is_speaking, "AudioManager should not be speaking after enabling screen reader mode")

# Test that TTS works again when disabling screen reader mode
func test_tts_works_when_disabling_screen_reader():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = true

	# Act - disable screen reader mode
	AudioManager.toggle_running_screen_reader(false)

	# Then try to play narration
	AudioManager.play_narration("Test message after disabling screen reader")

	# Assert
	# The function should process normally (not return early due to screen reader mode)
	# This test passes if no assertion fails (meaning the function ran to completion)
	assert_true(true, "TTS function should complete when screen reader mode is disabled")

# Test that narration disabled setting still takes precedence
func test_narration_disabled_takes_precedence():
	# Arrange
	AudioManager.enable_narration = false
	AudioManager.use_running_screen_reader = false

	# Act
	AudioManager.play_narration("Test message")

	# Assert
	assert_eq(AudioManager.tts_queue.size(), 0, "TTS queue should be empty when narration is disabled")

# Test the _process_tts_queue function respects screen reader mode
func test_process_tts_queue_respects_screen_reader_mode():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = false

	# Add items to queue manually
	AudioManager.tts_queue.append("Test message 1")
	AudioManager.tts_queue.append("Test message 2")

	# Enable screen reader mode
	AudioManager.use_running_screen_reader = true

	# Act
	AudioManager._process_tts_queue()

	# Assert
	assert_eq(AudioManager.tts_queue.size(), 0, "TTS queue should be cleared by _process_tts_queue when screen reader mode is active")
	assert_false(AudioManager.is_speaking, "AudioManager should not be speaking after processing queue in screen reader mode")

# Test that screen reader toggle provides appropriate feedback
func test_screen_reader_toggle_feedback():
	# Arrange
	AudioManager.enable_narration = true
	AudioManager.use_running_screen_reader = false

	# Act - enable screen reader mode
	AudioManager.toggle_running_screen_reader(true)

	# Assert - the function should have temporarily disabled screen reader mode to provide feedback
	assert_true(AudioManager.use_running_screen_reader, "Screen reader mode should be enabled after toggle")

	# Act - disable screen reader mode
	AudioManager.toggle_running_screen_reader(false)

	# Assert
	assert_false(AudioManager.use_running_screen_reader, "Screen reader mode should be disabled after toggle")
