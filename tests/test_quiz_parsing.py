#!/usr/bin/env python3
"""
Test script to verify quiz parsing functionality
"""

import json
import os
from app import DocumentProcessor

def test_quiz_parsing():
    """Test quiz parsing with both DOCX files"""
    
    # Test with Folktale-Reader file  
    docx_path1 = "Folktale-Reader-Descubra-Historias-Desbloqueie-Conhecimento.docx"
    json_path1 = "FolktaleReaderDescubraHistoriasDesbloqueieConhecimento.json"
    
    if os.path.exists(docx_path1):
        print(f"🧪 Testing quiz parsing with {docx_path1}")
        
        processor1 = DocumentProcessor(docx_path1, json_path1)
        
        # Force reconvert to test the new parsing logic
        if processor1.force_reconvert_docx():
            print("✅ Reconversion successful!")
            
            # Load and check the quiz content
            if os.path.exists(json_path1):
                with open(json_path1, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                quiz_count = 0
                for story_id, story in data.get('stories', {}).items():
                    for chapter_id, chapter in story.get('chapters', {}).items():
                        quiz_questions = chapter.get('quiz', [])
                        quiz_count += len(quiz_questions)
                        if quiz_questions:
                            print(f"📝 Story {story_id}, Chapter {chapter_id}: {len(quiz_questions)} quiz questions")
                            for i, q in enumerate(quiz_questions[:2]):  # Show first 2 questions
                                print(f"   Q{i+1}: {q.get('question', 'No question')}")
                                print(f"   Options: {len(q.get('options', []))} | Correct: {q.get('correct', 'None')}")
                
                print(f"🎯 Total quiz questions extracted: {quiz_count}")
        else:
            print("❌ Reconversion failed!")
    else:
        print(f"📄 File {docx_path1} not found")
    
    print("\n" + "="*60 + "\n")
    
    # Test with Brazilian Folktales file
    docx_path2 = "Brazilian Folktales.docx"
    json_path2 = "BrazilianFolktales.json"
    
    if os.path.exists(docx_path2):
        print(f"🧪 Testing quiz parsing with {docx_path2}")
        
        processor2 = DocumentProcessor(docx_path2, json_path2)
        
        # Force reconvert to test the new parsing logic
        if processor2.force_reconvert_docx():
            print("✅ Reconversion successful!")
            
            # Load and check the quiz content
            if os.path.exists(json_path2):
                with open(json_path2, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                quiz_count = 0
                for story_id, story in data.get('stories', {}).items():
                    for chapter_id, chapter in story.get('chapters', {}).items():
                        quiz_questions = chapter.get('quiz', [])
                        quiz_count += len(quiz_questions)
                        if quiz_questions:
                            print(f"📝 Story {story_id}, Chapter {chapter_id}: {len(quiz_questions)} quiz questions")
                            for i, q in enumerate(quiz_questions[:2]):  # Show first 2 questions
                                print(f"   Q{i+1}: {q.get('question', 'No question')}")
                                print(f"   Options: {len(q.get('options', []))} | Correct: {q.get('correct', 'None')}")
                
                print(f"🎯 Total quiz questions extracted: {quiz_count}")
        else:
            print("❌ Reconversion failed!")
    else:
        print(f"📄 File {docx_path2} not found")

if __name__ == "__main__":
    test_quiz_parsing()
