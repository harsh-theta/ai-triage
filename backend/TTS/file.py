from TTS.utils.synthesizer import Synthesizer

synthesizer = Synthesizer(
    tts_checkpoint="best_model.pth",
    tts_config_path="config.json",
    tts_speakers_file=f'speakers.pth',
)

text = "This is an Indian English voice using Griffin-Lim vocoder."
output_path = "output.wav"


# Save output using Griffin-Lim
wav = synthesizer.tts("Hello user, I am a medical assistant. How can I help you today?", speaker_name="female")
synthesizer.save_wav(wav, output_path)
