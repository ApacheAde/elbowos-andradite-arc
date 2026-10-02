# Andradite Arc

Full-colour Python 3 neon curved-rail shard catcher for [ElbowOS](https://x.com/ElbowOS).

Slide a teal gem along a molten gold arc and fire bolts through falling andradite shards. Wine-plum kiln, coral/lime/ice gems, spinning deflector rings. Not a ROM, not an emulator, original rules and art.

Left / Right (or A / D) slide the rail. Space fires a bolt. R restarts.

## Play

```bash
pip install -r requirements.txt
python3 andradite_arc.py --play
```

## Record a 9:16 reel

```bash
python3 andradite_arc.py --record
```

Writes a 1080x1920 h264 clip (15s @ 30fps, yuv420p, CRF 20, +faststart) with title, score, and `x.com/ElbowOS` burned into the frames. Headless path uses `SDL_VIDEODRIVER=dummy`.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1FgwaxvzGZlK0wmSasOBOGvc2fy0XgwN4/view?usp=drivesdk
