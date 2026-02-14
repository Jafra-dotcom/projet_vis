"""
Data Viz LLM - Version Ollama Mistral (Local)
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_csv, get_dataframe_info
from utils.validator import validate_dataframe
from llm.analyzer import DataVizAnalyzer
from llm.viz_proposer import VizProposer
from llm.code_generator import CodeGenerator
from visualization.plotter import VisualizationPlotter
from visualization.export import export_figure_to_bytes


st.set_page_config(page_title="Data Viz LLM - Mistral Local", page_icon="📊", layout="wide")


def init_session():
    """Init session state"""
    for key in ['df', 'df_info', 'analysis', 'proposals', 'selected_proposal', 'final_figure']:
        if key not in st.session_state:
            st.session_state[key] = None


def main():
    init_session()
    
    st.title("📊 Data Viz LLM - Mistral Local")
    st.markdown("**Génération automatique de visualisations avec Ollama Mistral (100% gratuit)**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        ollama_url = st.text_input("URL Ollama", value="http://localhost:11434")
        st.success("✅ Mistral local (pas de clé API)")
        st.info("Assurez-vous qu'Ollama est lancé:\n```bash\nollama serve\nollama run mistral\n```")
    
    # 1. Upload CSV
    st.header("1️⃣ Données")
    uploaded = st.file_uploader("CSV", type=['csv'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Exemple: Immobilier"):
            st.session_state.df = pd.read_csv("examples/example1_housing.csv")
    with col2:
        if st.button("Exemple: Ventes"):
            st.session_state.df = pd.read_csv("examples/example2_sales.csv")
    with col3:
        if st.button("Exemple: Climat"):
            st.session_state.df = pd.read_csv("examples/example3_climate.csv")
    
    if uploaded:
        st.session_state.df = load_csv(uploaded)
    
    if st.session_state.df is not None:
        is_valid, errors = validate_dataframe(st.session_state.df)
        if not is_valid:
            st.error("❌ " + ", ".join(errors))
            st.stop()
        
        st.session_state.df_info = get_dataframe_info(st.session_state.df)
        st.success(f"✅ {st.session_state.df.shape[0]} lignes, {st.session_state.df.shape[1]} colonnes")
        
        with st.expander("Aperçu"):
            st.dataframe(st.session_state.df.head())
        
        # 2. Question
        st.header("2️⃣ Problématique")
        question = st.text_area("Question", placeholder="Ex: Quels facteurs influencent le prix ?")
        
        if st.button("🔍 Analyser", type="primary"):
            if not question:
                st.warning("⚠️ Saisissez une question")
            else:
                with st.spinner("Analyse en cours..."):
                    try:
                        analyzer = DataVizAnalyzer(ollama_url)
                        st.session_state.analysis = analyzer.analyze_question(
                            question, st.session_state.df, st.session_state.df_info
                        )
                        
                        proposer = VizProposer(ollama_url)
                        st.session_state.proposals = proposer.propose_visualizations(
                            question, st.session_state.df_info, st.session_state.analysis
                        )
                        
                        st.success("✅ 3 propositions générées")
                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")
                        st.info("Vérifiez qu'Ollama est lancé: `ollama serve`")
        
        # 3. Propositions
        if st.session_state.proposals:
            st.header("3️⃣ Propositions")
            
            cols = st.columns(3)
            for idx, prop in enumerate(st.session_state.proposals[:3]):
                with cols[idx]:
                    st.subheader(f"Option {prop['id']}")
                    st.write(f"**{prop['type']}**")
                    st.write(f"📊 {prop['title']}")
                    st.write(f"X: {prop['x_axis']}")
                    st.write(f"Y: {prop['y_axis']}")
                    
                    if st.button(f"Sélectionner", key=f"sel_{idx}"):
                        st.session_state.selected_proposal = prop
                        st.rerun()
        
        # 4. Visualisation
        if st.session_state.selected_proposal:
            st.header("4️⃣ Visualisation")
            
            with st.spinner("Génération..."):
                try:
                    generator = CodeGenerator(ollama_url)
                    code = generator.generate_plot_code(
                        st.session_state.selected_proposal,
                        st.session_state.df_info
                    )
                    
                    plotter = VisualizationPlotter()
                    fig = plotter.execute_plot_code(code, st.session_state.df)
                    
                    if fig is None:
                        fig = plotter.create_fallback_visualization(
                            st.session_state.df,
                            st.session_state.selected_proposal['x_axis'],
                            st.session_state.selected_proposal['y_axis'],
                            st.session_state.selected_proposal['title']
                        )
                    
                    st.session_state.final_figure = fig
                except Exception as e:
                    st.error(f"Erreur: {e}")
            
            if st.session_state.final_figure:
                st.plotly_chart(st.session_state.final_figure, use_container_width=True)
                
                try:
                    img_bytes = export_figure_to_bytes(st.session_state.final_figure)
                    if img_bytes:
                        st.download_button(
                            "⬇️ Télécharger PNG",
                            data=img_bytes,
                            file_name="visualization.png",
                            mime="image/png",
                            type="primary"
                        )
                except:
                    pass
                
                if st.button("🔄 Nouvelle analyse"):
                    for key in ['analysis', 'proposals', 'selected_proposal', 'final_figure']:
                        st.session_state[key] = None
                    st.rerun()


if __name__ == "__main__":
    main()
