from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_cors import CORS
import json
import os
import re
from docx import Document
import PyPDF2
from gtts import gTTS
import tempfile
import uuid
from datetime import datetime
import hashlib
import secrets
from pathlib import Path
from config.settings import config
from database import (init_database, authenticate_user, get_user_by_id, create_user, get_all_users,
                      log_user_activity, get_user_achievements, get_user_achievement_stats,
                      get_global_ranking, get_user_rank, get_category_rankings)

# Initialize Flask app with proper configuration
app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

# Enable CORS
CORS(app)

# Configure static folder
app.static_folder = 'static'

# Initialize database
init_database()

def is_admin():
    """Check if current user is administrator"""
    return session.get('user_type') == 'admin'

def is_logged_in():
    """Check if user is logged in"""
    return session.get('user_id') is not None

def login_required(f):
    """Decorator for routes that require login"""
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return jsonify({'error': 'Login required.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def login_required_admin(f):
    """Decorator para rotas que requerem login de admin"""
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return jsonify({'error': 'Access denied. Admin login required.'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class FolktaleApp:
    def __init__(self):
        self.stories = {}
        self.user_progress = {}
        # Use proper data directory paths
        self.data_dir = Path(__file__).parent / "data"
        self.assets_dir = Path(__file__).parent / "assets"
        self.json_file = self.data_dir / 'stories_data.json'
        self.docx_file = self.assets_dir / 'BrazilianFolktales.docx'
        self.load_content()
    
    def load_content(self):
        """Carrega histórias do JSON ou converte do DOCX se necessário"""
        try:
            # Verifica se JSON existe e se é mais recente que o DOCX
            if self.should_use_json():
                self.load_from_json()
                print("Histórias carregadas do JSON")
            else:
                # Converte DOCX para JSON
                if self.docx_file.exists():
                    print("Convertendo DOCX para JSON...")
                    self.convert_docx_to_json()
                    self.load_from_json()
                    print("DOCX convertido para JSON e carregado")
                else:
                    self.load_example_stories()
                    self.save_to_json()
                    print("Histórias de exemplo salvas em JSON")
        except Exception as e:
            print(f"Erro ao carregar conteúdo: {e}")
            self.load_example_stories()
    
    def should_use_json(self):
        """Verifica se deve usar JSON existente ou reconverter do DOCX"""
        if not self.json_file.exists():
            return False
        
        if not self.docx_file.exists():
            return True
        
        # Compara datas de modificação
        json_time = self.json_file.stat().st_mtime
        docx_time = self.docx_file.stat().st_mtime
        
        # Se DOCX é mais recente, reconverte
        return json_time >= docx_time
    
    def load_from_json(self):
        """Loads stories from JSON file"""
        try:
            with open(str(self.json_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both old and new JSON formats
                if 'stories' in data:
                    self.stories = data['stories']
                else:
                    # Fallback for old format
                    self.stories = data
                
                # Convert string keys to int
                self.stories = {int(k): v for k, v in self.stories.items()}
                for story in self.stories.values():
                    if 'chapters' in story:
                        story['chapters'] = {int(k): v for k, v in story['chapters'].items()}
                
                # Print conversion info if available
                if 'conversion_info' in data:
                    conv_info = data['conversion_info']
                    print(f"Loaded {conv_info.get('stories_count', len(self.stories))} stories from {conv_info.get('source_file', 'unknown source')}")
                    print(f"Last conversion: {conv_info.get('conversion_timestamp', 'unknown')}")
                else:
                    print(f"Loaded {len(self.stories)} stories from JSON")
                    
        except Exception as e:
            print(f"Error loading JSON: {e}")
            raise
    
    def save_to_json(self):
        """Saves stories to JSON file with metadata"""
        try:
            # Include conversion metadata
            conversion_info = {
                'conversion_timestamp': datetime.now().isoformat(),
                'source_file': self.docx_file if os.path.exists(self.docx_file) else 'example_data',
                'stories_count': len(self.stories),
                'docx_last_modified': datetime.fromtimestamp(os.path.getmtime(self.docx_file)).isoformat() if os.path.exists(self.docx_file) else None
            }
            
            data = {
                'stories': self.stories,
                'conversion_info': conversion_info,
                'version': '2.0'
            }
            
            with open(str(self.json_file), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"Stories saved to {self.json_file} ({len(self.stories)} stories)")
        except Exception as e:
            print(f"Error saving JSON: {e}")
            raise
    
    def convert_docx_to_json(self):
        """Converts DOCX to JSON format"""
        try:
            print(f"Converting {self.docx_file} to JSON...")
            
            # Clear existing stories before conversion
            self.stories = {}
            
            doc = Document(self.docx_file)
            self.parse_docx_content(doc)
            self.save_to_json()
            
            print(f"Conversion completed. Found {len(self.stories)} stories.")
        except Exception as e:
            print(f"Error converting DOCX: {e}")
            raise
    
    def force_reconvert_docx(self):
        """Forces DOCX reconversion to JSON, clearing existing data"""
        if os.path.exists(self.docx_file):
            print(f"Forcing reconversion of {self.docx_file}...")
            
            # Clear existing stories data
            self.stories = {}
            
            # Remove existing JSON file to ensure clean conversion
            if os.path.exists(self.json_file):
                try:
                    os.remove(self.json_file)
                    print(f"Removed existing {self.json_file}")
                except OSError as e:
                    print(f"Warning: Could not remove existing JSON file: {e}")
            
            # Convert DOCX to new JSON
            self.convert_docx_to_json()
            print("DOCX successfully reconverted to new JSON file")
            return True
        else:
            print(f"DOCX file not found: {self.docx_file}")
            return False
    
    def parse_docx_content(self, doc):
        """Parse do documento DOCX para extrair histórias, quizzes e vocabulário"""
        # Initialize state variables for multi-line quiz parsing
        self._pending_question = None
        self._pending_options = []
        self._pending_correct = -1
        
        current_story = None
        current_chapter = None
        current_section = None
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            
            # Detecta nova história (título principal)
            if self.is_story_title(paragraph):
                story_id = len(self.stories) + 1
                current_story = {
                    'id': story_id,
                    'title': text,
                    'chapters': {},
                    'total_chapters': 0
                }
                self.stories[story_id] = current_story
                current_chapter = None
                current_section = None
            
            # Detecta capítulo
            elif self.is_chapter_title(text):
                if current_story:
                    chapter_num = self.extract_chapter_number(text)
                    current_story['chapters'][chapter_num] = {
                        'title': text,
                        'content': '',
                        'quiz': [],
                        'vocabulary': []
                    }
                    current_story['total_chapters'] = max(current_story['total_chapters'], chapter_num)
                    current_chapter = chapter_num
                    current_section = 'content'
            
            # Detecta seção de vocabulário
            elif self.is_vocabulary_section(text):
                if current_story and current_chapter:
                    current_section = 'vocabulary'
            
            # Detecta seção de quiz ou conteúdo que pode conter quiz
            elif 'quiz' in text.lower() or 'question' in text.lower() or self.contains_quiz_elements(text):
                if current_story and current_chapter:
                    current_section = 'quiz'
                    # Processa imediatamente se contém elementos de quiz
                    if self.contains_quiz_elements(text):
                        self.parse_quiz_question(text, current_story['chapters'][current_chapter]['quiz'])
            
            # Adiciona conteúdo
            elif current_story and current_chapter:
                if current_section == 'content':
                    current_story['chapters'][current_chapter]['content'] += text + '\n'
                elif current_section == 'vocabulary':
                    self.parse_vocabulary_entry(text, current_story['chapters'][current_chapter]['vocabulary'])
                elif current_section == 'quiz':
                    self.parse_quiz_question(text, current_story['chapters'][current_chapter]['quiz'])
    
    def is_story_title(self, paragraph):
        """Detecta se é título de história"""
        if not paragraph.runs:
            return False
        return (paragraph.runs[0].bold and len(paragraph.text.strip()) < 50) or paragraph.text.isupper()
    
    def is_chapter_title(self, text):
        """Detecta se é título de capítulo"""
        return bool(re.match(r'chapter\s+\d+', text.lower()) or re.match(r'capítulo\s+\d+', text.lower()))
    
    def contains_quiz_elements(self, text):
        """Detecta se o texto contém elementos de quiz (questões ou opções)"""
        text = text.strip()
        return bool(
            # Numbered questions
            re.match(r'^\d+\.', text) or
            # Option letters
            re.match(r'^[A-D]\)', text) or
            # Answer markers
            '✅' in text or
            '[resposta:' in text.lower() or
            # Question patterns
            ('Q:' in text and '?' in text) or
            # Multiple choice indicators
            ('A)' in text and 'B)' in text)
        )
    
    def extract_chapter_number(self, text):
        """Extrai número do capítulo"""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 1
    
    def is_vocabulary_section(self, text):
        """Detecta se é seção de vocabulário"""
        vocabulary_keywords = ['vocabulary', 'vocabulário', 'key words', 'palavras-chave', 'glossary']
        return any(keyword in text.lower() for keyword in vocabulary_keywords)
    
    def parse_vocabulary_entry(self, text, vocabulary_list):
        """Parse de entrada de vocabulário do DOCX"""
        # Formatos suportados:
        # "- word = tradução"
        # "word: tradução"
        # "word - tradução"
        # "word = tradução"
        
        # Remove marcadores de lista
        text = re.sub(r'^[-•*]\s*', '', text.strip())
        
        # Tenta diferentes separadores
        separators = [' = ', ': ', ' - ', ' – ', ' → ', ' -> ']
        
        for separator in separators:
            if separator in text:
                parts = text.split(separator, 1)
                if len(parts) == 2:
                    word = parts[0].strip()
                    translation = parts[1].strip()
                    
                    # Remove caracteres extras
                    word = re.sub(r'[^\w\s]', '', word).strip()
                    translation = re.sub(r'[^\w\s]', '', translation).strip()
                    
                    if word and translation and len(word) > 1:
                        # Busca contexto no conteúdo do capítulo (se disponível)
                        context = f"Used in the context of this chapter."
                        
                        vocabulary_list.append({
                            'word': word.capitalize(),
                            'translation': translation.lower(),
                            'context': context
                        })
                    break
    
    def parse_quiz_question(self, text, quiz_list):
        """Enhanced quiz parsing supporting multiple formats"""
        text = text.strip()
        if not text:
            return
            
        # Format 1: New format with numbered questions and ✅ markers
        # Example: "1. What is Boitatá?\n   a) A dog\n   b) A snake made of fire ✅\n   c) A bird"
        if re.match(r'^\d+\.', text):
            lines = text.split('\n')
            question_line = lines[0]
            
            # Extract question
            question_match = re.match(r'^\d+\.\s*(.+?)(?:\?|$)', question_line)
            if not question_match:
                return
                
            question = question_match.group(1).strip()
            if not question.endswith('?'):
                question += '?'
            
            # Extract options from subsequent lines
            options = []
            correct_index = -1
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                # Match option patterns: a) text ✅ or a) text
                option_match = re.match(r'^[a-d]\)\s*(.+?)(?:\s*✅)?$', line)
                if option_match:
                    option_text = option_match.group(1).strip()
                    options.append(option_text)
                    
                    # Check if this is the correct answer
                    if '✅' in line:
                        correct_index = len(options) - 1
            
            # Add question if we have enough options and a correct answer
            if len(options) >= 2 and correct_index >= 0:
                quiz_list.append({
                    'question': question,
                    'options': options,
                    'correct': correct_index
                })
                return
        
        # Format 2: Old format with [resposta: X] pattern
        # Example: "Q: How many legs does the Saci have? A) Two B) One C) Three [resposta: B]"
        if 'Q:' in text or ('?' in text and any(marker in text for marker in ['A)', 'B)', 'C)', 'D)'])):
            question_data = {
                'question': '',
                'options': [],
                'correct': 0
            }
            
            # Extract question
            if '?' in text:
                question_data['question'] = text.split('?')[0].strip()
                if 'Q:' in question_data['question']:
                    question_data['question'] = question_data['question'].split('Q:')[1].strip()
                question_data['question'] += '?'
                
                rest = text.split('?', 1)[1] if '?' in text else text
                
                # Extract options using regex
                options = re.findall(r'[A-D]\)\s*([^A-D\[]+)', rest)
                question_data['options'] = [opt.strip() for opt in options[:4]]
                
                # Extract correct answer
                correct_match = re.search(r'resposta:\s*([A-D])', text.lower())
                if correct_match:
                    correct_letter = correct_match.group(1).upper()
                    question_data['correct'] = ord(correct_letter) - ord('A')
                
                if len(question_data['options']) >= 2:
                    quiz_list.append(question_data)
                    return
        
        # Format 3: Multi-line format where options are on separate lines
        # Look for questions that might be split across multiple paragraphs
        if '?' in text and not any(marker in text for marker in ['A)', 'B)', 'C)', 'D)']):
            # This might be a question header, store it for potential combination with following options
            self._pending_question = text.strip()
            if not self._pending_question.endswith('?'):
                self._pending_question += '?'
            return
            
        # Check if this line contains options for a pending question
        if hasattr(self, '_pending_question') and self._pending_question:
            # Look for option patterns
            if re.match(r'^[A-D]\)', text) or '✅' in text:
                if not hasattr(self, '_pending_options'):
                    self._pending_options = []
                    self._pending_correct = -1
                
                option_match = re.match(r'^[A-D]\)\s*(.+?)(?:\s*✅)?$', text)
                if option_match:
                    option_text = option_match.group(1).strip()
                    self._pending_options.append(option_text)
                    
                    if '✅' in text:
                        self._pending_correct = len(self._pending_options) - 1
                
                # If we have enough options, create the quiz question
                if len(self._pending_options) >= 2 and self._pending_correct >= 0:
                    quiz_list.append({
                        'question': self._pending_question,
                        'options': self._pending_options,
                        'correct': self._pending_correct
                    })
                    
                    # Reset pending data
                    self._pending_question = None
                    self._pending_options = []
                    self._pending_correct = -1
    
    def load_example_stories(self):
        """Carrega histórias de exemplo com estrutura de capítulos"""
        self.stories = {
            1: {
                'id': 1,
                'title': 'The Legend of Curupira',
                'total_chapters': 3,
                'chapters': {
                    1: {
                        'title': 'Chapter 1: The Forest Guardian',
                        'content': '''Deep in the heart of the Amazon rainforest lives a mysterious creature known as Curupira. This legendary being has been protecting the forest for thousands of years. The Curupira appears as a small man with bright red hair and feet that point backward.

The backward feet are not just a curious feature - they serve a very important purpose. When hunters try to track the Curupira, they follow his footprints in the wrong direction, getting lost deeper in the forest instead of finding him.

Indigenous tribes have passed down stories of the Curupira from generation to generation. They say he appears to those who threaten the forest, leading them astray until they promise to respect nature.''',
                        'quiz': [
                            {
                                'question': 'What is the most distinctive feature of Curupira\'s feet?',
                                'options': ['They are very large', 'They point backward', 'They are golden', 'They glow in the dark'],
                                'correct': 1
                            },
                            {
                                'question': 'Why does Curupira have backward feet?',
                                'options': ['To run faster', 'To confuse hunters tracking him', 'To climb trees better', 'To swim in rivers'],
                                'correct': 1
                            }
                        ],
                        'vocabulary': [
                            {
                                'word': 'Forest',
                                'translation': 'floresta',
                                'context': 'Deep in the heart of the Amazon rainforest lives a mysterious creature.'
                            },
                            {
                                'word': 'Creature',
                                'translation': 'criatura',
                                'context': 'Deep in the heart of the Amazon rainforest lives a mysterious creature known as Curupira.'
                            },
                            {
                                'word': 'Mysterious',
                                'translation': 'misterioso',
                                'context': 'Deep in the heart of the Amazon rainforest lives a mysterious creature known as Curupira.'
                            },
                            {
                                'word': 'Protecting',
                                'translation': 'protegendo',
                                'context': 'This legendary being has been protecting the forest for thousands of years.'
                            },
                            {
                                'word': 'Backward',
                                'translation': 'para trás',
                                'context': 'The Curupira appears as a small man with bright red hair and feet that point backward.'
                            },
                            {
                                'word': 'Hunters',
                                'translation': 'caçadores',
                                'context': 'When hunters try to track the Curupira, they follow his footprints in the wrong direction.'
                            }
                        ]
                    },
                    2: {
                        'title': 'Chapter 2: The Lost Loggers',
                        'content': '''One day, a group of illegal loggers entered the sacred forest with their chainsaws and trucks. They planned to cut down the oldest trees to sell the valuable wood. But they did not know that the Curupira was watching.

As soon as the loggers started their work, strange things began to happen. Their compasses spun wildly, pointing in all directions. The forest paths they had marked disappeared overnight. They heard the sound of chainsaws coming from empty clearings.

The Curupira appeared to them as a small boy, seeming lost and frightened. "Can you help me find my way home?" he asked innocently. The loggers, thinking they could easily help and then continue their work, agreed to guide him.''',
                        'quiz': [
                            {
                                'question': 'What did the illegal loggers want to do in the forest?',
                                'options': ['Plant new trees', 'Cut down old trees', 'Study animals', 'Build a camp'],
                                'correct': 1
                            },
                            {
                                'question': 'How did Curupira first appear to the loggers?',
                                'options': ['As a giant monster', 'As a small lost boy', 'As an angry warrior', 'As a talking animal'],
                                'correct': 1
                            }
                        ]
                    },
                    3: {
                        'title': 'Chapter 3: The Lesson Learned',
                        'content': '''For three days and nights, the loggers followed the small boy deeper into the forest. Every path he took led them in circles. Every direction he pointed took them further from their trucks and equipment.

On the third night, exhausted and scared, the loggers realized they were completely lost. That's when the boy revealed his true identity. His hair turned bright red, and when they looked down, they saw his feet pointing backward.

"I am Curupira, guardian of this forest," he said. "You came here to destroy my home, but now you are lost in it. I will show you the way out, but only if you promise never to harm any forest again."

The loggers, understanding the power of nature and the importance of the forest, promised to change their ways. The Curupira guided them safely back to civilization, and they became forest protectors instead of destroyers.''',
                        'quiz': [
                            {
                                'question': 'How long were the loggers lost in the forest?',
                                'options': ['One day', 'Two days', 'Three days', 'One week'],
                                'correct': 2
                            },
                            {
                                'question': 'What did the loggers promise to do?',
                                'options': ['Return with more equipment', 'Never harm any forest again', 'Tell no one about Curupira', 'Pay money to the tribe'],
                                'correct': 1
                            }
                        ]
                    }
                }
            },
            2: {
                'id': 2,
                'title': 'The Pink Dolphin\'s Secret',
                'total_chapters': 3,
                'chapters': {
                    1: {
                        'title': 'Chapter 1: The River Festival',
                        'content': '''Every year, the village of Alter do Chão celebrates the Festival of the Waters. People from all along the Amazon River come to dance, sing, and celebrate the gifts of the river. The festival lasts for three nights, and each night brings new surprises.

Maria was eighteen years old and had never missed a festival. She loved to dance and was known throughout the village for her beautiful voice. This year, she wore her grandmother's white dress and flowers in her dark hair.

As the music began on the first night, a handsome young man appeared at the edge of the dance area. He wore elegant clothes and a stylish hat, but no one in the village recognized him. He had smooth skin, charming eyes, and a mysterious smile.''',
                        'quiz': [
                            {
                                'question': 'How often does the Festival of the Waters happen?',
                                'options': ['Every month', 'Every year', 'Every season', 'Every week'],
                                'correct': 1
                            },
                            {
                                'question': 'What was Maria known for in the village?',
                                'options': ['Her cooking', 'Her beautiful voice', 'Her painting', 'Her fishing skills'],
                                'correct': 1
                            }
                        ]
                    },
                    2: {
                        'title': 'Chapter 2: The Mysterious Dancer',
                        'content': '''The stranger approached Maria and asked her to dance. His movements were fluid like water, and he danced as if he had been born in the river itself. All night long, they danced together, and Maria felt as though she was floating on the water.

When dawn approached, the mysterious man said he had to leave. "I must return to my home before the sun rises," he explained. "But I will come back tomorrow night." He kissed her hand and disappeared into the morning mist near the river.

The next night, he returned as promised. Again, they danced until dawn, and again he left before sunrise. Maria noticed that he never removed his hat, even while dancing, and that his skin felt cool like river water.''',
                        'quiz': [
                            {
                                'question': 'How did the stranger dance?',
                                'options': ['Clumsily', 'Fluid like water', 'Very fast', 'Like a bird'],
                                'correct': 1
                            },
                            {
                                'question': 'What did Maria notice about the stranger?',
                                'options': ['He had warm skin', 'He never removed his hat', 'He wore no shoes', 'He spoke strangely'],
                                'correct': 1
                            }
                        ]
                    },
                    3: {
                        'title': 'Chapter 3: The Truth Revealed',
                        'content': '''On the third night, Maria was determined to learn the truth about her mysterious dancer. When he arrived, she danced closely and watched him carefully. In the moonlight, she noticed that his skin had a slight pink glow, and when he breathed, she could hear a soft whistling sound.

As dawn approached and he prepared to leave, Maria followed him quietly to the river. She hid behind the trees and watched in amazement as the handsome man walked into the water. As soon as the river reached his waist, his human form began to change.

His elegant clothes dissolved into the water, his arms became flippers, and his body transformed into that of a beautiful pink dolphin. The hat fell away, revealing a blowhole on top of his head. Maria realized she had been dancing with the legendary Boto, the pink river dolphin who could take human form.

The Boto sensed her presence and turned to look at her with intelligent, gentle eyes. Without fear, Maria stepped into the shallow water. The dolphin swam close to her and touched her hand with his nose, as if saying goodbye. Then he disappeared into the deep waters of the Amazon.

Maria never saw her mysterious dancer again, but every year at the festival, she would dance by the river's edge, hoping he might return.''',
                        'quiz': [
                            {
                                'question': 'What did Maria notice about the stranger\'s skin?',
                                'options': ['It was very dry', 'It had a slight pink glow', 'It was covered in scales', 'It was very dark'],
                                'correct': 1
                            },
                            {
                                'question': 'What happened to the stranger when he entered the river?',
                                'options': ['He swam away as a human', 'He transformed into a pink dolphin', 'He disappeared completely', 'He called for help'],
                                'correct': 1
                            }
                        ]
                    }
                }
            }
        }
    
    def get_story_list(self):
        """Retorna lista de histórias para exibição"""
        return [{'id': sid, 'title': story['title'], 'chapters': story['total_chapters']} 
                for sid, story in self.stories.items()]
    
    def get_chapter(self, story_id, chapter_num):
        """Retorna capítulo específico"""
        if story_id in self.stories and chapter_num in self.stories[story_id]['chapters']:
            return self.stories[story_id]['chapters'][chapter_num]
        return None
    
    def extract_vocabulary(self, story_id, chapter_num):
        """Extrai vocabulário útil do capítulo com traduções"""
        chapter = self.get_chapter(story_id, chapter_num)
        if not chapter:
            return []
        
        # Primeiro, verifica se há vocabulário definido no DOCX
        if 'vocabulary' in chapter and chapter['vocabulary']:
            # Adiciona contexto do conteúdo para vocabulário do DOCX
            for vocab_item in chapter['vocabulary']:
                if 'context' not in vocab_item or vocab_item['context'] == "Used in the context of this chapter.":
                    vocab_item['context'] = self.get_word_context(chapter['content'], vocab_item['word'])
            return chapter['vocabulary']
        
        # Se não há vocabulário no DOCX, extrai automaticamente
        return self.extract_automatic_vocabulary(chapter['content'])
    
    def extract_automatic_vocabulary(self, text):
        """Extrai vocabulário automaticamente do texto"""
    def extract_automatic_vocabulary(self, text):
        """Extrai vocabulário automaticamente do texto"""
        # Dicionário de vocabulário com traduções contextuais
        vocabulary_dict = {
            # Curupira vocabulary
            'forest': 'floresta',
            'creature': 'criatura',
            'mysterious': 'misterioso',
            'legendary': 'lendário',
            'protecting': 'protegendo',
            'backward': 'para trás',
            'footprints': 'pegadas',
            'hunters': 'caçadores',
            'indigenous': 'indígena',
            'tribes': 'tribos',
            'generation': 'geração',
            'threaten': 'ameaçar',
            'respect': 'respeitar',
            'nature': 'natureza',
            'illegal': 'ilegal',
            'loggers': 'madeireiros',
            'chainsaws': 'motosserras',
            'valuable': 'valioso',
            'compasses': 'bússolas',
            'wildly': 'descontroladamente',
            'directions': 'direções',
            'paths': 'caminhos',
            'disappeared': 'desapareceram',
            'overnight': 'durante a noite',
            'clearings': 'clareiras',
            'innocently': 'inocentemente',
            'exhausted': 'exaustos',
            'frightened': 'assustados',
            'revealed': 'revelou',
            'identity': 'identidade',
            'guardian': 'guardião',
            'destroy': 'destruir',
            'civilization': 'civilização',
            'protectors': 'protetores',
            
            # Pink Dolphin vocabulary
            'festival': 'festival',
            'celebrate': 'celebrar',
            'gifts': 'presentes',
            'charming': 'encantador',
            'elegant': 'elegante',
            'stylish': 'elegante',
            'recognized': 'reconheceu',
            'mysterious': 'misterioso',
            'stranger': 'estranho',
            'approached': 'se aproximou',
            'movements': 'movimentos',
            'fluid': 'fluido',
            'floating': 'flutuando',
            'dawn': 'amanhecer',
            'approached': 'se aproximou',
            'disappear': 'desaparecer',
            'mist': 'névoa',
            'promised': 'prometeu',
            'removed': 'removeu',
            'determination': 'determinação',
            'truth': 'verdade',
            'closely': 'de perto',
            'moonlight': 'luar',
            'glow': 'brilho',
            'whistling': 'assobiando',
            'prepared': 'se preparou',
            'followed': 'seguiu',
            'quietly': 'silenciosamente',
            'amazement': 'espanto',
            'waist': 'cintura',
            'transform': 'transformar',
            'dissolved': 'se dissolveu',
            'flippers': 'nadadeiras',
            'blowhole': 'respiradouro',
            'dolphin': 'golfinho',
            'sensed': 'percebeu',
            'presence': 'presença',
            'intelligent': 'inteligente',
            'gentle': 'gentil',
            'shallow': 'raso',
            'touched': 'tocou',
            'goodbye': 'adeus',
            
            # Common vocabulary
            'heart': 'coração',
            'lives': 'vive',
            'appears': 'aparece',
            'bright': 'brilhante',
            'hair': 'cabelo',
            'point': 'apontar',
            'curious': 'curioso',
            'feature': 'característica',
            'serve': 'servir',
            'purpose': 'propósito',
            'track': 'rastrear',
            'follow': 'seguir',
            'wrong': 'errado',
            'direction': 'direção',
            'getting': 'ficando',
            'lost': 'perdido',
            'deeper': 'mais fundo',
            'instead': 'ao invés de',
            'finding': 'encontrando',
            'passed': 'passaram',
            'down': 'para baixo',
            'stories': 'histórias',
            'leading': 'conduzindo',
            'astray': 'desviado',
            'until': 'até',
            'promise': 'prometer',
            'group': 'grupo',
            'entered': 'entrou',
            'sacred': 'sagrado',
            'trucks': 'caminhões',
            'planned': 'planejaram',
            'oldest': 'mais velhas',
            'trees': 'árvores',
            'sell': 'vender',
            'wood': 'madeira',
            'watching': 'observando',
            'started': 'começaram',
            'work': 'trabalho',
            'strange': 'estranho',
            'things': 'coisas',
            'began': 'começaram',
            'happen': 'acontecer',
            'spinning': 'girando',
            'pointing': 'apontando',
            'marked': 'marcaram',
            'heard': 'ouviram',
            'sound': 'som',
            'coming': 'vindo',
            'empty': 'vazias',
            'appeared': 'apareceu',
            'small': 'pequeno',
            'seeming': 'parecendo',
            'help': 'ajudar',
            'find': 'encontrar',
            'home': 'casa',
            'asked': 'perguntou',
            'thinking': 'pensando',
            'could': 'poderiam',
            'easily': 'facilmente',
            'continue': 'continuar',
            'agreed': 'concordaram',
            'guide': 'guiar'
        }
        
        # Extrai palavras do texto
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Filtra palavras muito comuns
        common_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 
            'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 
            'see', 'two', 'way', 'who', 'boy', 'did', 'she', 'use', 'her', 'how', 'said', 'each', 'make', 
            'most', 'over', 'such', 'very', 'what', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 
            'good', 'much', 'some', 'time', 'well', 'were'
        }
        
        # Seleciona vocabulário útil
        vocabulary = []
        seen = set()
        
        for word in words:
            if (word in vocabulary_dict and 
                word not in common_words and 
                word not in seen and 
                len(word) > 2):
                
                vocabulary.append({
                    'word': word.capitalize(),
                    'translation': vocabulary_dict[word],
                    'context': self.get_word_context(text, word)
                })
                seen.add(word)
                
                if len(vocabulary) >= 12:  # Limita a 12 palavras por capítulo
                    break
        
        return vocabulary
    
    def get_word_context(self, text, word):
        """Extrai contexto da palavra no texto"""
        sentences = text.split('.')
        for sentence in sentences:
            if word.lower() in sentence.lower():
                return sentence.strip() + '.'
        return f"Used in the story about {word}."
    
    def get_user_progress(self, user_id):
        """Retorna progresso do usuário"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                'stories_completed': {},
                'total_quiz_attempts': 0,
                'total_correct_answers': 0,
                'current_story': None,
                'current_chapter': 1,
                'badges': [],
                'start_date': datetime.now().isoformat()
            }
        return self.user_progress[user_id]
    
    def update_progress(self, user_id, story_id, chapter_num, quiz_score, total_questions):
        """Atualiza progresso do usuário"""
        progress = self.get_user_progress(user_id)
        progress['total_quiz_attempts'] += 1
        progress['total_correct_answers'] += quiz_score
        
        story_key = f"story_{story_id}"
        if story_key not in progress['stories_completed']:
            progress['stories_completed'][story_key] = {'chapters_completed': [], 'quiz_scores': {}}
        
        chapter_key = f"chapter_{chapter_num}"
        progress['stories_completed'][story_key]['quiz_scores'][chapter_key] = {
            'score': quiz_score,
            'total': total_questions,
            'percentage': round((quiz_score / total_questions) * 100),
            'date': datetime.now().isoformat()
        }
        
        # Se passou no quiz (70% ou mais), marca capítulo como completo
        if (quiz_score / total_questions) >= 0.7:
            if chapter_num not in progress['stories_completed'][story_key]['chapters_completed']:
                progress['stories_completed'][story_key]['chapters_completed'].append(chapter_num)
        
        # Verifica badges
        self.check_and_award_badges(user_id, progress)
        
        return progress
    
    def check_and_award_badges(self, user_id, progress):
        """Sistema de badges/conquistas"""
        badges = progress.get('badges', [])
        
        # Badge: Primeiro capítulo
        if 'first_chapter' not in badges and progress['total_quiz_attempts'] >= 1:
            badges.append('first_chapter')
        
        # Badge: História completa
        completed_stories = 0
        for story_data in progress['stories_completed'].values():
            if len(story_data['chapters_completed']) >= 3:  # História completa
                completed_stories += 1
        
        if 'story_master' not in badges and completed_stories >= 1:
            badges.append('story_master')
        
        # Badge: Quiz expert (80% de acertos)
        if progress['total_quiz_attempts'] > 0:
            accuracy = progress['total_correct_answers'] / progress['total_quiz_attempts']
            if 'quiz_expert' not in badges and accuracy >= 0.8 and progress['total_quiz_attempts'] >= 10:
                badges.append('quiz_expert')
        
        progress['badges'] = badges

# Inicializa a aplicação
folktale_app = FolktaleApp()

@app.route('/')
def index():
    # Gera ID único para sessão se não existir
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user login"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    # Authenticate user using database
    success, user_data = authenticate_user(username, password)
    
    if success:
        # Set session data
        session['user_id'] = user_data['id']
        session['username'] = user_data['username']
        session['user_type'] = user_data['user_type']
        session['login_time'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': user_data['username'],
            'user_type': user_data['user_type'],
            'is_admin': user_data['is_admin']
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """API endpoint for logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@app.route('/api/auth_status')
def auth_status():
    """API endpoint to check authentication status"""
    user_id = session.get('user_id')
    if user_id:
        user_data = get_user_by_id(user_id)
        if user_data:
            return jsonify({
                'authenticated': True,
                'is_admin': user_data['is_admin'],
                'username': user_data['username'],
                'user_type': user_data['user_type'],
                'login_time': session.get('login_time')
            })
    
    return jsonify({
        'authenticated': False,
        'is_admin': False,
        'username': None,
        'user_type': None,
        'login_time': None
    })

@app.route('/api/demo/stories')
def get_demo_stories():
    """Public API endpoint to show sample stories on welcome screen"""
    # Return only basic information for demonstration
    demo_stories = []
    for story_id, story in folktale_app.stories.items():
        demo_stories.append({
            'id': story_id,
            'title': story['title'],
            'chapters': story['total_chapters'],
            'description': f"A fascinating Brazilian folktale with {story['total_chapters']} interactive chapters.",
            'duration': f"~{story['total_chapters'] * 5} minutes"
        })
    
    return jsonify(demo_stories[:3])  # Only first 3 for demo

@app.route('/api/demo/sample')
def get_demo_sample():
    """Public API endpoint to show a sample chapter"""
    # Get first chapter of first story as example
    if folktale_app.stories:
        first_story = list(folktale_app.stories.values())[0]
        if first_story['chapters']:
            first_chapter = first_story['chapters'][1]
            # Return only a preview of the content
            content_preview = first_chapter['content'][:400] + "..."
            return jsonify({
                'title': first_story['title'],
                'chapter_title': first_chapter['title'],
                'text': content_preview
            })
    
    # Fallback if no stories available
    return jsonify({
        'title': 'The Legend of Curupira',
        'chapter_title': 'The Forest Guardian',
        'text': 'Deep in the Amazon rainforest, where ancient trees reach toward the sky and mysterious sounds echo through the canopy, there lived a creature known as Curupira. This magical being was the guardian of the forest, protector of all animals and plants...'
    })

@app.route('/api/admin/create_demo_users', methods=['POST'])
@login_required_admin
def create_demo_users():
    """Create demonstration users (admin only)"""
    demo_users = [
        {'username': 'student1', 'password': 'demo123', 'user_type': 'regular'},
        {'username': 'student2', 'password': 'demo123', 'user_type': 'regular'},
        {'username': 'teacher1', 'password': 'teacher123', 'user_type': 'regular'},
    ]
    
    created_users = []
    errors = []
    
    for user_data in demo_users:
        success, message = create_user(
            user_data['username'], 
            user_data['password'], 
            user_data['user_type']
        )
        
        if success:
            created_users.append(user_data['username'])
        else:
            errors.append(f"{user_data['username']}: {message}")
    
    return jsonify({
        'success': True,
        'created_users': created_users,
        'errors': errors
    })

@app.route('/api/admin/users')
@login_required_admin
def get_all_users_endpoint():
    """Get all users (admin only)"""
    users = get_all_users()
    # Remove sensitive information
    safe_users = []
    for user in users:
        safe_users.append({
            'id': user['id'],
            'username': user['username'],
            'user_type': user['user_type'],
            'created_at': user['created_at'],
            'last_login': user['last_login'],
            'is_active': user['is_active']
        })
    
    return jsonify(safe_users)

@app.route('/api/demo/chapter_sample')
def get_demo_chapter():
    """API endpoint público para mostrar um trecho de exemplo"""
    # Pega o primeiro capítulo da primeira história como exemplo
    if folktale_app.stories:
        first_story = list(folktale_app.stories.values())[0]
        if first_story['chapters']:
            first_chapter = first_story['chapters'][1]
            # Retorna apenas um trecho do conteúdo
            content_preview = first_chapter['content'][:300] + "..."
            return jsonify({
                'title': first_chapter['title'],
                'preview': content_preview,
                'full_content_available': True
            })
    
    return jsonify({
        'title': 'Exemplo de Capítulo',
        'preview': 'Aqui você encontrará histórias fascinantes em inglês...',
        'full_content_available': False
    })

@app.route('/api/stories')
@login_required
def get_stories():
    """API endpoint para listar todas as histórias"""
    return jsonify(folktale_app.get_story_list())

@app.route('/api/story/<int:story_id>/chapter/<int:chapter_num>')
@login_required
def get_chapter(story_id, chapter_num):
    """API endpoint para obter capítulo específico"""
    chapter = folktale_app.get_chapter(story_id, chapter_num)
    if chapter:
        # Log chapter reading activity for achievements
        try:
            new_achievements = log_user_activity(session['user_id'], 'chapter_read', {
                'story_id': story_id,
                'chapter_num': chapter_num,
                'title': chapter.get('title', '')
            })
            chapter['new_achievements'] = new_achievements
        except Exception as e:
            print(f"Achievement logging error: {e}")
            chapter['new_achievements'] = []
        
        return jsonify(chapter)
    return jsonify({'error': 'Chapter not found'}), 404

@app.route('/api/audio/<int:story_id>/<int:chapter_num>')
def get_audio(story_id, chapter_num):
    """API endpoint para gerar áudio do capítulo"""
    chapter = folktale_app.get_chapter(story_id, chapter_num)
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    try:
        # Gera áudio usando gTTS
        tts = gTTS(text=chapter['content'], lang='en', slow=False)
        
        # Salva em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        return send_file(temp_file.name, as_attachment=True, 
                        download_name=f'chapter_{story_id}_{chapter_num}.mp3',
                        mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': f'Audio generation failed: {str(e)}'}), 500

@app.route('/api/quiz/<int:story_id>/<int:chapter_num>')
def get_chapter_quiz(story_id, chapter_num):
    """API endpoint para obter quiz do capítulo"""
    chapter = folktale_app.get_chapter(story_id, chapter_num)
    if chapter and 'quiz' in chapter:
        return jsonify(chapter['quiz'])
    return jsonify({'error': 'Quiz not found'}), 404

@app.route('/api/vocabulary/<int:story_id>/<int:chapter_num>')
def get_chapter_vocabulary(story_id, chapter_num):
    """API endpoint para obter vocabulário do capítulo"""
    vocabulary = folktale_app.extract_vocabulary(story_id, chapter_num)
    if vocabulary:
        return jsonify(vocabulary)
    return jsonify({'error': 'Chapter not found'}), 404

@app.route('/api/submit_quiz', methods=['POST'])
def submit_quiz():
    """API endpoint para submeter respostas do quiz"""
    if 'user_id' not in session:
        return jsonify({'error': 'No session found'}), 400
    
    data = request.get_json()
    story_id = data.get('story_id')
    chapter_num = data.get('chapter_num')
    answers = data.get('answers', [])
    
    # Verifica respostas
    chapter = folktale_app.get_chapter(story_id, chapter_num)
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    quiz = chapter.get('quiz', [])
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    score = 0
    results = []
    
    for i, answer in enumerate(answers):
        if i < len(quiz):
            correct = quiz[i]['correct']
            is_correct = answer == correct
            if is_correct:
                score += 1
            
            results.append({
                'question_index': i,
                'user_answer': answer,
                'correct_answer': correct,
                'is_correct': is_correct,
                'question': quiz[i]['question']
            })
    
    # Atualiza progresso do usuário
    progress = folktale_app.update_progress(session['user_id'], story_id, chapter_num, score, len(quiz))
    
    # Verifica se pode avançar (70% ou mais de acertos)
    can_advance = (score / len(quiz)) >= 0.7
    percentage = round((score / len(quiz)) * 100)
    
    # Log quiz activity for achievements
    try:
        new_achievements = log_user_activity(session['user_id'], 'quiz_completed', {
            'story_id': story_id,
            'chapter_num': chapter_num,
            'score': score,
            'total': len(quiz),
            'percentage': percentage,
            'can_advance': can_advance
        })
    except Exception as e:
        new_achievements = []
        print(f"Achievement logging error: {e}")
    
    return jsonify({
        'score': score,
        'total': len(quiz),
        'percentage': percentage,
        'can_advance': can_advance,
        'results': results,
        'progress': progress,
        'new_achievements': new_achievements
    })

@app.route('/api/progress')
@login_required
def get_user_progress():
    """API endpoint para obter progresso do usuário"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    progress = folktale_app.get_user_progress(session['user_id'])
    return jsonify(progress)

@app.route('/api/statistics')
@login_required
def get_statistics():
    """API endpoint para estatísticas detalhadas"""
    if 'user_id' not in session:
        return jsonify({'error': 'No session found'}), 400
    
    progress = folktale_app.get_user_progress(session['user_id'])
    
    # Calcula estatísticas
    stats = {
        'total_stories': len(folktale_app.stories),
        'stories_started': len(progress['stories_completed']),
        'stories_finished': 0,
        'total_chapters_completed': 0,
        'quiz_attempts': progress['total_quiz_attempts'],
        'correct_answers': progress['total_correct_answers'],
        'accuracy_percentage': 0,
        'badges': progress['badges'],
        'recent_scores': [],
        'chapter_breakdown': {}
    }
    
    # Analisa histórias completadas
    for story_key, story_data in progress['stories_completed'].items():
        chapters_completed = len(story_data['chapters_completed'])
        stats['total_chapters_completed'] += chapters_completed
        
        if chapters_completed >= 3:  # História completa (assumindo 3 capítulos)
            stats['stories_finished'] += 1
        
        # Scores recentes
        for chapter_key, quiz_data in story_data['quiz_scores'].items():
            stats['recent_scores'].append({
                'story': story_key,
                'chapter': chapter_key,
                'percentage': quiz_data['percentage'],
                'date': quiz_data['date']
            })
        
        stats['chapter_breakdown'][story_key] = {
            'chapters_completed': chapters_completed,
            'total_chapters': 3,  # Assumindo 3 capítulos por história
            'completion_percentage': round((chapters_completed / 3) * 100)
        }
    
    # Ordena scores por data (mais recentes primeiro)
    stats['recent_scores'].sort(key=lambda x: x['date'], reverse=True)
    stats['recent_scores'] = stats['recent_scores'][:10]  # Últimos 10
    
    # Calcula precisão
    if stats['quiz_attempts'] > 0:
        stats['accuracy_percentage'] = round((stats['correct_answers'] / stats['quiz_attempts']) * 100)
    
    return jsonify(stats)

@app.route('/api/reload_docx', methods=['POST'])
@login_required_admin
def reload_docx():
    """API endpoint to force DOCX reconversion, replacing existing JSON"""
    try:
        print("Starting forced DOCX reconversion...")
        
        # Get old story count for comparison
        old_stories_count = len(folktale_app.stories)
        
        success = folktale_app.force_reconvert_docx()
        if success:
            # Reload the stories from new JSON
            folktale_app.load_from_json()
            new_stories_count = len(folktale_app.stories)
            
            return jsonify({
                'success': True, 
                'message': f'DOCX successfully reconverted to new JSON',
                'old_stories_count': old_stories_count,
                'new_stories_count': new_stories_count,
                'stories_changed': new_stories_count != old_stories_count,
                'conversion_timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'DOCX file not found: {folktale_app.docx_file}'
            }), 404
    except Exception as e:
        print(f"Error during DOCX reconversion: {e}")
        return jsonify({
            'success': False, 
            'message': f'Error converting DOCX: {str(e)}'
        }), 500

@app.route('/api/data_info')
@login_required_admin
def get_data_info():
    """API endpoint for information about loaded data"""
    try:
        info = {
            'json_exists': os.path.exists(folktale_app.json_file),
            'docx_exists': os.path.exists(folktale_app.docx_file),
            'stories_count': len(folktale_app.stories),
            'source': 'unknown',
            'json_file': folktale_app.json_file,
            'docx_file': folktale_app.docx_file
        }
        
        # Check JSON file info
        if os.path.exists(folktale_app.json_file):
            json_time = datetime.fromtimestamp(folktale_app.json_file.stat().st_mtime)
            info['json_last_modified'] = json_time.isoformat()
            info['json_size_kb'] = round(folktale_app.json_file.stat().st_size / 1024, 2)
            
            # Try to read conversion info from JSON
            try:
                with open(str(folktale_app.json_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'conversion_info' in data:
                        info['conversion_info'] = data['conversion_info']
            except:
                pass
        
        # Check DOCX file info
        if folktale_app.docx_file.exists():
            docx_time = datetime.fromtimestamp(folktale_app.docx_file.stat().st_mtime)
            info['docx_last_modified'] = docx_time.isoformat()
            info['docx_size_kb'] = round(folktale_app.docx_file.stat().st_size / 1024, 2)
        
        # Determine data source
        if info['json_exists'] and info['docx_exists']:
            if folktale_app.json_file.stat().st_mtime >= folktale_app.docx_file.stat().st_mtime:
                info['source'] = 'json (up to date)'
                info['needs_reconversion'] = False
            else:
                info['source'] = 'docx (newer than json)'
                info['needs_reconversion'] = True
        elif info['json_exists']:
            info['source'] = 'json only'
            info['needs_reconversion'] = False
        elif info['docx_exists']:
            info['source'] = 'docx only'
            info['needs_reconversion'] = True
        else:
            info['source'] = 'example data'
            info['needs_reconversion'] = False
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/json')
@login_required_admin
def download_json():
    """Download do arquivo JSON atual"""
    try:
        if os.path.exists(folktale_app.json_file):
            return send_file(folktale_app.json_file, as_attachment=True, 
                           download_name='stories_data.json',
                           mimetype='application/json')
        else:
            return jsonify({'error': 'Arquivo JSON não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Achievement API Endpoints
@app.route('/api/achievements')
@login_required
def get_achievements():
    """Get all achievements for current user"""
    try:
        user_id = session.get('user_id')
        achievements = get_user_achievements(user_id)
        return jsonify(achievements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/achievements/stats')
@login_required
def get_achievement_stats():
    """Get achievement statistics for current user"""
    try:
        user_id = session.get('user_id')
        stats = get_user_achievement_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log_activity', methods=['POST'])
@login_required
def log_activity():
    """Log user activity and check for new achievements"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        activity_type = data.get('activity_type')
        activity_data = data.get('activity_data', {})
        
        # Log the activity and check achievements
        new_achievements = log_user_activity(user_id, activity_type, activity_data)
        
        return jsonify({
            'success': True,
            'new_achievements': new_achievements
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ranking API Endpoints
@app.route('/api/ranking/global')
@login_required
def get_global_leaderboard():
    """Get global ranking leaderboard"""
    try:
        limit = request.args.get('limit', 50, type=int)
        ranking = get_global_ranking(limit)
        return jsonify(ranking)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ranking/user')
@login_required
def get_user_ranking():
    """Get current user's rank"""
    try:
        user_id = session.get('user_id')
        user_rank = get_user_rank(user_id)
        return jsonify(user_rank)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ranking/categories')
@login_required
def get_category_leaderboards():
    """Get rankings by achievement categories"""
    try:
        rankings = get_category_rankings()
        return jsonify(rankings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)