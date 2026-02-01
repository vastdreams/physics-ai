# ai/equational/
"""
Research Ingestion Engine.

Inspired by DREAM architecture - ingest research papers and extract equations.

First Principle Analysis:
- Ingestion: Parse PDF/LaTeX/Markdown → Extract text → Identify equations
- Sources: ArXiv, PDF files, LaTeX documents
- Mathematical foundation: Document parsing, text extraction, pattern matching
- Architecture: Modular ingestion with multiple format support
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class ResearchPaper:
    """Represents a research paper."""
    paper_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    content: str = ""
    equations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=datetime.now)


class ResearchIngestion:
    """
    Research ingestion engine.
    
    Features:
    - PDF parsing
    - LaTeX parsing
    - ArXiv integration
    - Equation extraction
    - Metadata extraction
    """
    
    def __init__(self):
        """Initialize research ingestion engine."""
        self.logger = SystemLogger()
        self.papers: Dict[str, ResearchPaper] = {}
        
        self.logger.log("ResearchIngestion initialized", level="INFO")
    
    def ingest_pdf(self, file_path: str) -> Optional[ResearchPaper]:
        """
        Ingest PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ResearchPaper instance or None
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="INGEST_PDF",
            input_data={'file_path': file_path},
            level=LogLevel.INFO
        )
        
        try:
            # Try PyMuPDF first (better quality)
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                content = ""
                for page in doc:
                    content += page.get_text()
                doc.close()
            except ImportError:
                # Fallback to PyPDF2
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text()
                except Exception as e:
                    self.logger.log(f"Error parsing PDF: {str(e)}", level="ERROR")
                    cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
                    return None
            
            # Extract metadata
            paper_id = f"paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            paper = ResearchPaper(
                paper_id=paper_id,
                title=file_path.split('/')[-1],
                content=content,
                metadata={'source': 'pdf', 'file_path': file_path}
            )
            
            self.papers[paper_id] = paper
            
            cot.end_step(step_id, output_data={'paper_id': paper_id}, validation_passed=True)
            
            self.logger.log(f"PDF ingested: {paper_id}", level="INFO")
            
            return paper
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error ingesting PDF: {str(e)}", level="ERROR")
            return None
    
    def ingest_arxiv(self, arxiv_id: str) -> Optional[ResearchPaper]:
        """
        Ingest paper from ArXiv.
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            ResearchPaper instance or None
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="INGEST_ARXIV",
            input_data={'arxiv_id': arxiv_id},
            level=LogLevel.INFO
        )
        
        try:
            try:
                import arxiv
                search = arxiv.Search(id_list=[arxiv_id])
                paper_list = list(search.results())
                
                if not paper_list:
                    cot.end_step(step_id, output_data={'error': 'Paper not found'}, validation_passed=False)
                    return None
                
                arxiv_paper = paper_list[0]
                
                paper = ResearchPaper(
                    paper_id=f"arxiv_{arxiv_id}",
                    title=arxiv_paper.title,
                    authors=[author.name for author in arxiv_paper.authors],
                    abstract=arxiv_paper.summary,
                    content=arxiv_paper.summary,  # Would download full text in production
                    metadata={
                        'source': 'arxiv',
                        'arxiv_id': arxiv_id,
                        'published': arxiv_paper.published.isoformat() if arxiv_paper.published else None
                    }
                )
                
                self.papers[paper.paper_id] = paper
                
                cot.end_step(step_id, output_data={'paper_id': paper.paper_id}, validation_passed=True)
                
                self.logger.log(f"ArXiv paper ingested: {paper.paper_id}", level="INFO")
                
                return paper
            
            except ImportError:
                self.logger.log("ArXiv library not installed", level="WARNING")
                cot.end_step(step_id, output_data={'error': 'ArXiv library not installed'}, validation_passed=False)
                return None
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error ingesting ArXiv paper: {str(e)}", level="ERROR")
            return None
    
    def ingest_latex(self, latex_content: str, paper_id: Optional[str] = None) -> Optional[ResearchPaper]:
        """
        Ingest LaTeX content.
        
        Args:
            latex_content: LaTeX document content
            paper_id: Optional paper ID
            
        Returns:
            ResearchPaper instance or None
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="INGEST_LATEX",
            input_data={'paper_id': paper_id},
            level=LogLevel.INFO
        )
        
        try:
            if not paper_id:
                paper_id = f"latex_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract title from \title{}
            import re
            title_match = re.search(r'\\title\{([^}]+)\}', latex_content)
            title = title_match.group(1) if title_match else "Untitled"
            
            # Extract authors from \author{}
            author_match = re.search(r'\\author\{([^}]+)\}', latex_content)
            authors = [author_match.group(1)] if author_match else []
            
            paper = ResearchPaper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                content=latex_content,
                metadata={'source': 'latex'}
            )
            
            self.papers[paper_id] = paper
            
            cot.end_step(step_id, output_data={'paper_id': paper_id}, validation_passed=True)
            
            self.logger.log(f"LaTeX ingested: {paper_id}", level="INFO")
            
            return paper
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error ingesting LaTeX: {str(e)}", level="ERROR")
            return None
    
    def get_paper(self, paper_id: str) -> Optional[ResearchPaper]:
        """Get paper by ID."""
        return self.papers.get(paper_id)
    
    def list_papers(self) -> List[Dict[str, Any]]:
        """List all ingested papers."""
        return [
            {
                'paper_id': paper.paper_id,
                'title': paper.title,
                'authors': paper.authors,
                'ingested_at': paper.ingested_at.isoformat()
            }
            for paper in self.papers.values()
        ]

