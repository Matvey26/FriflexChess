import os
import torch
import torchaudio
import numpy as np
import wave
from aksharamukha import transliterate
from .chess_notation import transliterate_chess_notation

TTS_CONFIG = {
    'en': dict(version='v3', language='en',   speaker='lj_16khz',    sample_rate=48000),
    'fr': dict(version='v3', language='fr',   speaker='gilles_16khz', sample_rate=48000),
    'es': dict(version='v3', language='es',   speaker='tux_16khz',    sample_rate=48000),
    'de': dict(version='v3', language='de',   speaker='thorsten_16khz',sample_rate=48000),
    'hi': dict(version='v3', language='indic',speaker='v4_indic',
               translit_from='Devanagari', translit_to='ISO',
               apply_speaker='hindi_male', sample_rate=48000),
    'ru': dict(
        version='v4',
        language='ru',
        model_id='v4_ru',
        apply_speaker='baya',
        sample_rate=48000,
    ),
}

class TTSEngine:
    def __init__(self):
        self.device = torch.device('cpu')
        torch.set_num_threads(4)
    
    def save_wav_via_wave(self, audio_tensor: torch.Tensor, sr: int, out_path: str):
        if audio_tensor.dim() == 1:
            audio_tensor = audio_tensor.unsqueeze(0)

        data = (audio_tensor.squeeze().cpu().numpy() * 32767).astype(np.int16)

        with wave.open(out_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(data.tobytes())

    def synthesize(self, text: str, lang: str, out_wav: str):
        cfg = TTS_CONFIG[lang]
        
        if lang == 'ru' and cfg.get('version') == 'v4':
            text = transliterate_chess_notation(text)

        if cfg.get('version') == 'v4':
            model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language=cfg['language'],
                speaker=cfg['model_id']
            )
            model.to(self.device)
            audio = model.apply_tts(
                text=text,
                speaker=cfg['apply_speaker'],
                sample_rate=cfg['sample_rate']
            )
            sr_use = cfg['sample_rate']
        else:
            res = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language=cfg['language'],
                speaker=cfg['speaker']
            )
            
            if isinstance(res, tuple) and len(res) == 5:
                model, symbols, sr, _, apply_fn = res
                model.to(self.device)
                audio = apply_fn([text], model, sr, symbols, self.device)[0]
                sr_use = sr
            else:
                model, _ = res
                model.to(self.device)
                if lang == 'hi':
                    roman = transliterate.process(cfg['translit_from'], cfg['translit_to'], text)
                    audio = model.apply_tts(roman, speaker=cfg['apply_speaker'])
                else:
                    audio = model.apply_tts(
                        text,
                        speaker=cfg['speaker'],
                        sample_rate=cfg['sample_rate']
                    )
                    if isinstance(audio, (list, tuple)):
                        audio = audio[0]
                sr_use = cfg['sample_rate']

        self.save_wav_via_wave(audio, sr_use, out_wav)
        
        if sr_use != 48000:
            resampler = torchaudio.transforms.Resample(sr_use, 48000)
            audio_48k = resampler(audio.unsqueeze(0)).squeeze(0)
            base, ext = os.path.splitext(out_wav)
            out_48k = f"{base}_48k{ext}"
            self.save_wav_via_wave(audio_48k, 48000, out_48k)