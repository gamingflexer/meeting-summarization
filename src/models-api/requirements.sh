pip install git+https://github.com/openai/whisper.git --no-deps
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
pip install -U scikit-learn scipy matplotlib
git clone https://github.com/maxent-ai/converse.git && cd converse && pip install -e . && cd ..
sudo apt install ffmpeg
sudo apt-get install libsndfile1-dev