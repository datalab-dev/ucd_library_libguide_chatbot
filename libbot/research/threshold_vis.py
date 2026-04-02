#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


def load_embeddings(embeddings_path):
    """Load embeddings from .npy file"""
    print(f"Loading corpus embeddings from {embeddings_path}...")
    embeddings = np.load(embeddings_path)
    print(f"Loaded embeddings shape: {embeddings.shape}")
    return embeddings


def compute_similarities(query_embedding, corpus_embeddings):
    """
    Compute cosine similarities between query and all corpus documents
    Returns sorted similarities (descending order)
    """
    # Reshape query if needed
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_embedding, corpus_embeddings)[0]
    
    # Sort in descending order
    sorted_similarities = np.sort(similarities)[::-1]
    
    return sorted_similarities


def get_query_embeddings(corpus_embeddings, query_mode='random', query_embeddings_path=None, n_queries=10):
    """
    Get query embeddings based on mode
    
    Args:
        corpus_embeddings: The corpus embeddings
        query_mode: 'random' (sample from corpus) or 'file' (load from file)
        query_embeddings_path: Path to query embeddings if mode='file'
        n_queries: Number of random queries if mode='random'
    
    Returns:
        Array of query embeddings
    """
    if query_mode == 'random':
        print(f"\nUsing {n_queries} random corpus documents as sample queries...")
        n_docs = corpus_embeddings.shape[0]
        query_indices = np.random.choice(n_docs, size=n_queries, replace=False)
        return corpus_embeddings[query_indices]
    
    elif query_mode == 'file':
        print(f"\nLoading query embeddings from {query_embeddings_path}...")
        query_embeddings = np.load(query_embeddings_path)
        print(f"Loaded {len(query_embeddings)} query embeddings")
        return query_embeddings
    
    else:
        raise ValueError(f"Unknown query_mode: {query_mode}")


def compute_all_similarities(query_embeddings, corpus_embeddings):
    """Compute similarities for all queries"""
    all_similarities = []
    
    print(f"\nComputing similarities for {len(query_embeddings)} queries...")
    for i, query_embedding in enumerate(query_embeddings):
        similarities = compute_similarities(query_embedding, corpus_embeddings)
        all_similarities.append(similarities)
        
        if (i + 1) % 5 == 0:
            print(f"Processed {i + 1}/{len(query_embeddings)} queries")
    
    return np.array(all_similarities)


def plot_similarity_curves(all_similarities, max_k=100):
    """
    Simple plots to visually identify cutoff points
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: All individual curves overlaid
    ax1 = axes[0]
    for i, similarities in enumerate(all_similarities):
        ax1.plot(range(1, min(max_k + 1, len(similarities) + 1)), 
                similarities[:max_k], alpha=0.4, linewidth=1.5)
    
    ax1.set_xlabel('Document Rank (k)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Cosine Similarity Score', fontsize=13, fontweight='bold')
    ax1.set_title(f'Similarity Decay for Each Query\n(Each line = 1 query)', 
                  fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.4)
    ax1.tick_params(labelsize=11)
    
    # Plot 2: Mean curve (the average pattern)
    ax2 = axes[1]
    mean_similarities = np.mean(all_similarities[:, :max_k], axis=0)
    x = range(1, max_k + 1)
    
    ax2.plot(x, mean_similarities, linewidth=3, color='darkblue', marker='o', 
             markersize=4, markevery=5)
    
    ax2.set_xlabel('Document Rank (k)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Average Cosine Similarity', fontsize=13, fontweight='bold')
    ax2.set_title('Average Similarity Decay Across All Queries', 
                  fontsize=15, fontweight='bold')
    ax2.grid(True, alpha=0.4)
    ax2.tick_params(labelsize=11)
    
    plt.tight_layout()
    return fig


def main():
    """Main analysis pipeline"""
    
    # ============= CONFIGURATION =============
    # Path to your corpus embeddings
    CORPUS_EMBEDDINGS_PATH = "/dsl/libbot/data/embeddings_qwen.npy"
    
    # Query mode: 'random' or 'file'
    # 'random' = randomly sample documents from corpus as queries (for testing)
    # 'file' = load actual query embeddings from a file
    QUERY_MODE = 'file'
    
    # If QUERY_MODE='file', provide path to query embeddings
    QUERY_EMBEDDINGS_PATH = "/dsl/libbot/data/embeddings_testing_prompts_extended.npy"
    
    # Number of queries (only used if QUERY_MODE='random')
    # N_QUERIES = 20
    
    # Maximum k to visualize
    MAX_K = 7442
    # =========================================
    
    # Check if corpus file exists
    if not Path(CORPUS_EMBEDDINGS_PATH).exists():
        print(f"ERROR: Corpus embeddings file not found: {CORPUS_EMBEDDINGS_PATH}")
        print("Please update CORPUS_EMBEDDINGS_PATH in the script")
        return
    
    # Load corpus embeddings
    corpus_embeddings = load_embeddings(CORPUS_EMBEDDINGS_PATH)
    
    # Get query embeddings
    query_embeddings = get_query_embeddings(
        corpus_embeddings, 
        query_mode=QUERY_MODE,
        query_embeddings_path=QUERY_EMBEDDINGS_PATH #if QUERY_MODE == 'file' else None,
        # n_queries=N_QUERIES
    )
    
    # Compute similarities for all queries
    all_similarities = compute_all_similarities(query_embeddings, corpus_embeddings)
    
    # Generate plots
    print("\nGenerating visualizations...")
    fig = plot_similarity_curves(all_similarities, MAX_K)
    
    # Print simple stats
    mean_sims = np.mean(all_similarities[:, :MAX_K], axis=0)
    
    print("\n" + "=" * 60)
    print("SIMILARITY STATISTICS")
    print("=" * 60)
    print(f"Queries analyzed: {len(query_embeddings)}")
    print(f"Corpus size: {len(corpus_embeddings)}")
    print(f"\nAverage similarity at different k values:")
    for k in [1, 5, 10, 20, 30, 50, 75, 100]:
        if k <= MAX_K:
            print(f"  k={k:3d}: {mean_sims[k-1]:.4f}")
    
    # Save plot
    output_path = "/dsl/libbot/data/plots_testing/rag_threshold_analysis_extended.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n Plot saved to: {output_path}")
    
    plt.show()


if __name__ == "__main__":
    main()