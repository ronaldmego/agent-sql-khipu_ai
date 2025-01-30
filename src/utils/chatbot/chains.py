from typing import Any, Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging

from config.config import OLLAMA_INSIGHTS_MODEL
from ...utils.database import get_schema, run_query
from .prompts import ChatbotPrompts
from ...utils.llm_provider import LLMProvider
import streamlit as st

logger = logging.getLogger(__name__)

class ChainBuilder:
    """Handles the creation and configuration of LangChain chains"""
    
    @staticmethod
    def _clean_sql_query(query: str) -> str:
        """Clean SQL query from markdown formatting and other artifacts"""
        # Remove markdown SQL markers
        query = query.replace('```sql', '').replace('```', '')
        
        # Remove any leading/trailing whitespace
        query = query.strip()
        
        # Ensure the query ends with a semicolon if it doesn't have one
        if not query.strip().endswith(';'):
            query += ';'
        
        return query

    @staticmethod
    def build_sql_chain():
        """Build the SQL generation chain"""
        try:
            prompt = ChatbotPrompts.get_sql_prompt()
            llm = LLMProvider.get_llm(
                provider=st.session_state.get('llm_provider', 'openai'),
                model_name=st.session_state.get('llm_model_name'),
                temperature=st.session_state.get('llm_temperature', 0.7)
            )
            
            return (
                RunnablePassthrough()
                | ChainBuilder._format_sql_input
                | prompt
                | llm.bind(stop=["\nSQLResult:"])
                | StrOutputParser()
                | ChainBuilder._clean_sql_query
            )
        except Exception as e:
            logger.error(f"Error building SQL chain: {str(e)}")
            raise

    @staticmethod
    def build_response_chain(sql_chain):
        """Build the response generation chain"""
        try:
            prompt = ChatbotPrompts.get_response_prompt()
            
            # Obtener el modelo OpenAI para el análisis principal
            main_llm = LLMProvider.get_llm(
                provider=st.session_state.get('llm_provider', 'openai'),
                model_name=st.session_state.get('llm_model_name'),
                temperature=st.session_state.get('llm_temperature', 0.7)
            )

            # Chain principal
            main_chain = (
                RunnablePassthrough().assign(
                    query=sql_chain,
                    schema=ChainBuilder._get_schema,
                    response=ChainBuilder._run_query,
                    temporal_analysis=ChainBuilder._analyze_temporal_patterns,
                    statistical_analysis=ChainBuilder._analyze_statistics,
                    comparative_analysis=ChainBuilder._analyze_comparisons
                )
                | ChainBuilder._process_enhanced_response
                | prompt 
                | main_llm 
                | StrOutputParser()
            )

            def process_complete_response(x):
                # Obtener la respuesta principal
                main_response = main_chain.invoke(x)
                
                # Separar la parte de visualización si existe
                viz_data = None
                if "DATA:" in main_response:
                    main_part, viz_part = main_response.split("DATA:", 1)
                    viz_data = "DATA:" + viz_part
                    main_response = main_part.strip()
                
                # Agregar el análisis crítico
                response_with_critical = ChainBuilder._add_critical_analysis(main_response)
                
                # Reincorporar los datos de visualización si existían
                if viz_data:
                    response_with_critical += "\n\n" + viz_data
                
                return response_with_critical
            
            return RunnablePassthrough() | process_complete_response

        except Exception as e:
            logger.error(f"Error building response chain: {str(e)}")
            raise

    @staticmethod
    def _add_critical_analysis(main_response: str) -> str:
        """Add critical analysis after main analysis completes"""
        try:
            # Obtener Deepseek para el análisis crítico
            critical_llm = LLMProvider.get_llm(
                provider="ollama",
                model_name=OLLAMA_INSIGHTS_MODEL,
                temperature=0.7
            )
            
            # Preprocesar el análisis principal para evitar caracteres problemáticos
            clean_response = main_response.replace('\n\n', '\n').strip()
            
            # Obtener el prompt desde ChatbotPrompts
            critical_prompt = ChatbotPrompts.get_critical_analysis_prompt()
            
            # Generar el análisis crítico
            try:
                critical_analysis = critical_llm.invoke(
                    critical_prompt.format_prompt(analysis=clean_response).to_string()
                )
                
                # Verificar que el análisis crítico sea válido antes de agregarlo
                if critical_analysis and isinstance(critical_analysis, str) and len(critical_analysis.strip()) > 50:
                    return f"{main_response}\n\n## 🐋 Análisis Crítico del Razonamiento\n{critical_analysis}"
                else:
                    logger.info("Critical analysis was too short or invalid - skipping")
                    return main_response
                    
            except Exception as inner_e:
                logger.info(f"Critical analysis generation failed - skipping: {str(inner_e)}")
                return main_response
                
        except Exception as e:
            logger.info(f"Critical analysis setup failed - skipping: {str(e)}")
            return main_response

    @staticmethod
    def _format_sql_input(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Format input for SQL prompt template"""
        try:
            selected_tables = vars.get("selected_tables", [])
            schema = get_schema(selected_tables)
            table_list = "'" + "','".join(selected_tables) + "'" if selected_tables else "''"
            return {
                "schema": schema,
                "question": vars["question"],
                "table_list": table_list
            }
        except Exception as e:
            logger.error(f"Error formatting SQL input: {str(e)}")
            raise

    @staticmethod
    def _get_schema(vars: Dict[str, Any]) -> str:
        """Get schema information for selected tables"""
        try:
            return get_schema(vars.get("selected_tables", []))
        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            raise

    @staticmethod
    def _run_query(vars: Dict[str, Any]) -> Any:
        """Execute SQL query"""
        try:
            query = vars.get("query")
            if not query:
                raise ValueError("No query provided")
            return run_query(query)
        except Exception as e:
            logger.error(f"Error running query: {str(e)}")
            raise

    @staticmethod
    def _analyze_temporal_patterns(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal patterns in the data"""
        try:
            schema = vars.get("schema", "")
            selected_tables = vars.get("selected_tables", [])
            if not (schema and selected_tables):
                return {}

            # Identificar columnas de fecha en cada tabla
            date_columns = {}
            for table in selected_tables:
                table_schema = [line for line in schema.split('\n') if table in line]
                for line in table_schema:
                    if any(date_type in line.lower() for date_type in ["date", "timestamp"]):
                        col_name = line.split()[0]
                        date_columns[f"{table}.{col_name}"] = col_name

            if not date_columns:
                return {}

            analysis = {}
            for table_col, date_col in date_columns.items():
                table = table_col.split('.')[0]
                try:
                    query = f"""
                    SELECT 
                        EXTRACT(YEAR FROM {date_col}) as year,
                        EXTRACT(MONTH FROM {date_col}) as month,
                        COUNT(*) as count
                    FROM {table}
                    GROUP BY 
                        EXTRACT(YEAR FROM {date_col}),
                        EXTRACT(MONTH FROM {date_col})
                    ORDER BY year, month
                    """
                    temporal_results = run_query(query)
                    analysis[table_col] = temporal_results
                except Exception as e:
                    logger.error(f"Error analyzing temporal patterns for {table_col}: {str(e)}")
                    continue

            return {"temporal_patterns": analysis}
        except Exception as e:
            logger.error(f"Error in temporal analysis: {str(e)}")
            return {}

    @staticmethod
    def _analyze_statistics(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on numerical columns"""
        try:
            schema = vars.get("schema", "")
            selected_tables = vars.get("selected_tables", [])
            if not (schema and selected_tables):
                return {}

            # Identificar columnas numéricas en cada tabla
            numeric_columns = {}
            for table in selected_tables:
                table_schema = [line for line in schema.split('\n') if table in line]
                for line in table_schema:
                    if any(num_type in line.lower() for num_type in ["int", "decimal", "float", "double"]):
                        col_name = line.split()[0]
                        numeric_columns[f"{table}.{col_name}"] = col_name

            if not numeric_columns:
                return {}

            analysis = {}
            for table_col, num_col in numeric_columns.items():
                table = table_col.split('.')[0]
                try:
                    query = f"""
                    SELECT 
                        AVG({num_col}) as mean,
                        STDDEV({num_col}) as std_dev,
                        MIN({num_col}) as min_val,
                        MAX({num_col}) as max_val,
                        COUNT(*) as count
                    FROM {table}
                    """
                    stats = run_query(query)
                    analysis[table_col] = stats
                except Exception as e:
                    logger.error(f"Error analyzing statistics for {table_col}: {str(e)}")
                    continue

            return {"statistical_summary": analysis}
        except Exception as e:
            logger.error(f"Error in statistical analysis: {str(e)}")
            return {}

    @staticmethod
    def _analyze_comparisons(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparative analysis between different categories/groups"""
        try:
            schema = vars.get("schema", "")
            selected_tables = vars.get("selected_tables", [])
            if not (schema and selected_tables):
                return {}

            # Identificar columnas categóricas en cada tabla
            categorical_columns = {}
            for table in selected_tables:
                table_schema = [line for line in schema.split('\n') if table in line]
                for line in table_schema:
                    if any(cat_type in line.lower() for cat_type in ["varchar", "char", "text"]):
                        col_name = line.split()[0]
                        categorical_columns[f"{table}.{col_name}"] = col_name

            if not categorical_columns:
                return {}

            analysis = {}
            for table_col, cat_col in categorical_columns.items():
                table = table_col.split('.')[0]
                try:
                    query = f"""
                    SELECT 
                        {cat_col},
                        COUNT(*) as count
                    FROM {table}
                    GROUP BY {cat_col}
                    ORDER BY count DESC
                    LIMIT 10
                    """
                    comparisons = run_query(query)
                    analysis[table_col] = comparisons
                except Exception as e:
                    logger.error(f"Error analyzing comparisons for {table_col}: {str(e)}")
                    continue

            return {"comparative_analysis": analysis}
        except Exception as e:
            logger.error(f"Error in comparative analysis: {str(e)}")
            return {}

    @staticmethod
    def _process_enhanced_response(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Process response before final prompt with enhanced analysis"""
        try:
            from .insights import InsightGenerator
            
            # Obtener insights básicos (mantener funcionalidad original)
            schema_data = InsightGenerator.get_default_insights(vars.get("selected_tables", []))
            schema_suggestions = InsightGenerator.generate_schema_suggestions(schema_data)
            
            # Combinar con análisis adicionales
            enhanced_vars = {
                "insights": schema_data,
                "suggestions": schema_suggestions,
                "rag_context": st.session_state.get('last_context', []),
                "temporal_analysis": vars.get("temporal_analysis", {}),
                "statistical_analysis": vars.get("statistical_analysis", {}),
                "comparative_analysis": vars.get("comparative_analysis", {}),
                "question": vars.get("question", ""),
                "query": vars.get("query", ""),
                "schema": vars.get("schema", ""),
                "response": vars.get("response", []),
                "selected_tables": vars.get("selected_tables", [])
            }
            
            # Evaluar respuesta si es string
            if isinstance(enhanced_vars["response"], str):
                try:
                    enhanced_vars["response"] = eval(enhanced_vars["response"])
                except:
                    pass

            return enhanced_vars
        except Exception as e:
            logger.error(f"Error processing enhanced response: {str(e)}")
            raise