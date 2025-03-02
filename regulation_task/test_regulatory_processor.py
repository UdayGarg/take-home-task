#!/usr/bin/env python
import os
import sys
import json
import pytest
import sqlite3
from pathlib import Path
import tempfile
import shutil

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from regulatory_compliance_processor.knowledge_base.document_store import DocumentStore
from regulatory_compliance_processor.knowledge_base.vector_store_factory import VectorStoreFactory
from regulatory_compliance_processor.analysis.compliance_analyzer import ComplianceAnalyzer
from regulatory_compliance_processor.config import DOCUMENT_DB_PATH, VECTOR_DB_PATH


class TestDatabaseExistence:
    """Tests for database existence and structure"""
    
    def test_document_db_path_exists(self):
        """Test that the document database directory exists"""
        db_dir = os.path.dirname(DOCUMENT_DB_PATH)
        assert os.path.exists(db_dir), f"Document database directory does not exist: {db_dir}"
    
    def test_vector_db_path_exists(self):
        """Test that the vector database directory exists"""
        assert os.path.exists(VECTOR_DB_PATH), f"Vector database directory does not exist: {VECTOR_DB_PATH}"


class TestDocumentStore:
    """Tests for DocumentStore functionality"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        yield temp_db_path
        
        # Cleanup after test
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
    
    def test_document_store_initialization(self, temp_db_path):
        """Test that DocumentStore initializes correctly"""
        doc_store = DocumentStore(db_path=temp_db_path)
        assert doc_store is not None
        assert os.path.exists(temp_db_path)
    
    def test_document_store_schema(self, temp_db_path):
        """Test that DocumentStore creates the correct schema"""
        # Initialize document store to create schema
        DocumentStore(db_path=temp_db_path)
        
        # Connect to the database and check schema
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Check required tables exist
        required_tables = ['documents', 'document_versions', 'regulatory_clauses', 'sop_analyses']
        for table in required_tables:
            assert table in tables, f"Table {table} not found in database schema"
        
        # Check columns in documents table
        cursor.execute(f"PRAGMA table_info(documents)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check required columns
        required_columns = ['id', 'file_name', 'title', 'source', 'document_type', 'added_date', 'last_updated', 'metadata', 'status']
        for column in required_columns:
            assert column in columns, f"Column {column} not found in documents table"
        
        conn.close()
    
    def test_add_and_retrieve_document(self, temp_db_path):
        """Test adding and retrieving a document"""
        doc_store = DocumentStore(db_path=temp_db_path)
        
        # Test data
        file_name = "test_regulation.pdf"
        content = "This is test content for a regulatory document."
        title = "Test Regulation"
        
        # Add document
        doc_id, version = doc_store.add_document(
            file_name=file_name,
            content=content,
            title=title,
            source="Test",
            document_type="Regulation"
        )
        
        # Retrieve document
        doc = doc_store.get_document(doc_id)
        
        # Verify document data
        assert doc is not None
        assert doc["file_name"] == file_name
        assert doc["title"] == title
        assert doc["version"]["content"] == content
        assert doc["version"]["number"] == 1
    
    def test_add_clauses_and_retrieve(self, temp_db_path):
        """Test adding and retrieving regulatory clauses"""
        doc_store = DocumentStore(db_path=temp_db_path)
        
        # Add a document
        doc_id, version = doc_store.add_document(
            file_name="test_regulation.pdf",
            content="Test content",
            title="Test Regulation"
        )
        
        # Create test clauses
        clauses = [
            {
                "section": "1.1",
                "title": "Test Clause 1",
                "text": "This is a test regulatory clause."
            },
            {
                "section": "1.2",
                "title": "Test Clause 2",
                "text": "This is another test regulatory clause."
            }
        ]
        
        # Add clauses
        doc_store.add_regulatory_clauses(doc_id, version, clauses)
        
        # Retrieve clauses
        retrieved_clauses = doc_store.get_regulatory_clauses(doc_id, version)
        
        # Verify clauses
        assert len(retrieved_clauses) == 2
        assert retrieved_clauses[0]["section"] == "1.1"
        assert retrieved_clauses[1]["section"] == "1.2"
        assert retrieved_clauses[0]["text"] == "This is a test regulatory clause."
    
    def test_delete_document(self, temp_db_path):
        """Test document deletion functionality"""
        doc_store = DocumentStore(db_path=temp_db_path)
        
        # Add a document with clauses
        doc_id, version = doc_store.add_document(
            file_name="to_delete.pdf",
            content="Content to delete",
            title="Document to Delete"
        )
        
        clauses = [{"section": "1", "text": "Test clause"}]
        doc_store.add_regulatory_clauses(doc_id, version, clauses)
        
        # Delete the document
        success, count = doc_store.completely_delete_document(doc_id)
        
        # Verify deletion
        assert success is True
        assert count == 1
        
        # Try to retrieve the deleted document
        doc = doc_store.get_document(doc_id)
        assert doc is None


class TestVectorStore:
    """Tests for VectorStore functionality"""
    
    @pytest.fixture
    def temp_vector_db_path(self):
        """Create a temporary vector database path for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_vector_store_factory_creation(self, temp_vector_db_path):
        """Test that VectorStoreFactory creates a vector store correctly"""
        vector_store = VectorStoreFactory.create_vector_store(
            use_langchain=True,
            vector_db_path=temp_vector_db_path
        )
        
        assert vector_store is not None
        # Should create a directory in the temp path for ChromaDB
        assert os.path.exists(temp_vector_db_path)
    
    def test_add_and_search_clauses(self, temp_vector_db_path):
        """Test adding clauses to vector store and searching"""
        vector_store = VectorStoreFactory.create_vector_store(
            use_langchain=True,
            vector_db_path=temp_vector_db_path
        )
        
        # Test clauses
        clauses = [
            {
                "document_id": 1,
                "document_version": 1,
                "section": "1.1",
                "text": "Safety equipment must be inspected regularly.",
                "source_document": "Test Regulation"
            },
            {
                "document_id": 1, 
                "document_version": 1,
                "section": "1.2",
                "text": "All employees must be trained on emergency procedures.",
                "source_document": "Test Regulation"
            }
        ]
        
        # Add clauses
        vector_store.add_clauses(clauses)
        
        # Search for related content
        results = vector_store.search("safety inspections", k=5)
        
        # Verify results - there should be at least one result with the first clause
        assert len(results) > 0
        # At least one result should contain "safety equipment" text
        safety_results = [r for r in results if "safety equipment" in r.get("text", "").lower()]
        assert len(safety_results) > 0


class TestComplianceAnalyzer:
    """Tests for ComplianceAnalyzer functionality"""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create a mock vector store for testing"""
        class MockVectorStore:
            def search(self, query, k=5):
                # Return mock search results
                return [
                    {
                        "id": 1,
                        "document_id": 1,
                        "text": "Safety equipment must be inspected regularly.",
                        "section": "1.1",
                        "source_document": "Test Regulation",
                        "similarity": 0.85
                    },
                    {
                        "id": 2,
                        "document_id": 1,
                        "text": "All employees must be trained on emergency procedures.",
                        "section": "1.2",
                        "source_document": "Test Regulation",
                        "similarity": 0.75
                    }
                ]
                
            def get_stats(self):
                return {"total_clauses": 2}
                
        return MockVectorStore()
    
    def test_analyzer_initialization(self, mock_vector_store):
        """Test ComplianceAnalyzer initialization"""
        analyzer = ComplianceAnalyzer(vector_store=mock_vector_store)
        assert analyzer is not None
        assert analyzer.vector_store is mock_vector_store
    
    @pytest.mark.skip(reason="Requires OpenAI API key and makes actual API calls")
    def test_extract_sop_sections(self, mock_vector_store):
        """Test extracting sections from SOP content"""
        analyzer = ComplianceAnalyzer(vector_store=mock_vector_store)
        
        # Simple SOP content for testing
        sop_text = """
        # Safety Procedures
        
        ## 1. Equipment Inspection
        All safety equipment must be inspected weekly.
        
        ## 2. Emergency Training
        All employees must complete emergency training annually.
        """
        
        # Extract sections
        sections = analyzer._extract_sop_sections(sop_text)
        
        # Verify sections
        assert len(sections) > 0
        # Should find the Equipment Inspection section
        equipment_sections = [s for s in sections if "equipment" in s.get("title", "").lower()]
        assert len(equipment_sections) > 0


class TestEndToEnd:
    """End-to-end tests for regulatory compliance processor"""
    
    @pytest.mark.skip(reason="Long-running test that requires actual documents")
    def test_regulatory_document_processing(self):
        """Test processing a sample regulatory document"""
        from regulatory_compliance_processor.document_processing.parsers import DocumentParserFactory
        
        # Check if we have sample data
        sample_doc_path = os.path.join("data", "regulations", "REG-ASTM D6400.pdf")
        if not os.path.exists(sample_doc_path):
            pytest.skip(f"Sample document not found: {sample_doc_path}")
        
        # Initialize parser
        parser_factory = DocumentParserFactory()
        
        # Parse document
        doc_content = parser_factory.parse_document(sample_doc_path)
        
        # Verify basic parsing results
        assert doc_content is not None
        assert "text" in doc_content
        assert len(doc_content["text"]) > 100  # Should have substantial text content
    
    @pytest.mark.skip(reason="Long-running test that requires OpenAI API calls")
    def test_compliance_analysis(self):
        """Test SOP compliance analysis process"""
        # Check if we have sample SOP
        sample_sop_path = os.path.join("data", "sop", "sop.docx")
        if not os.path.exists(sample_sop_path):
            pytest.skip(f"Sample SOP not found: {sample_sop_path}")
        
        # Initialize components
        document_store = DocumentStore()
        vector_store = VectorStoreFactory.create_vector_store()
        analyzer = ComplianceAnalyzer(vector_store=vector_store)
        
        # Parse SOP document
        parser_factory = DocumentParserFactory()
        sop_content = parser_factory.parse_document(sample_sop_path)
        sop_content["file_name"] = "sop.docx"  # Add filename for reports
        
        # Run compliance analysis
        compliance_report = analyzer.analyze_sop_compliance(sop_content)
        
        # Verify report structure
        assert compliance_report is not None
        assert "sop" in compliance_report
        assert "recommendations" in compliance_report
        assert "summary" in compliance_report


class TestConfigurationAndEnvironment:
    """Tests for configuration and environment variables"""
    
    def test_config_loading(self):
        """Test that configuration loads properly"""
        from regulatory_compliance_processor.config import (
            REGULATORY_DOCS_DIR, SOP_DIR, MAX_WORKERS, 
            USE_RULE_BASED_EXTRACTION, USE_HYBRID_EXTRACTION
        )
        
        # Verify key configuration values
        assert REGULATORY_DOCS_DIR is not None
        assert SOP_DIR is not None
        assert isinstance(MAX_WORKERS, int)
        assert isinstance(USE_RULE_BASED_EXTRACTION, bool)
        assert isinstance(USE_HYBRID_EXTRACTION, bool)
    
    def test_directories_exist(self):
        """Test that key directories exist"""
        from regulatory_compliance_processor.config import REGULATORY_DOCS_DIR, SOP_DIR, CACHE_DIR
        
        assert os.path.exists(REGULATORY_DOCS_DIR), f"Regulatory docs directory does not exist: {REGULATORY_DOCS_DIR}"
        assert os.path.exists(SOP_DIR), f"SOP directory does not exist: {SOP_DIR}"
        assert os.path.exists(CACHE_DIR), f"Cache directory does not exist: {CACHE_DIR}"


if __name__ == "__main__":
    pytest.main()