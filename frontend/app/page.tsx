"use client";

import { useEffect, useMemo, useState } from "react";
import axios from "axios";

type Repository = {
  id: number;
  name: string;
  github_url: string;
  local_path: string;
};

type AskContext = {
  file_path: string;
  file_type: string | null;
  chunk_index: number;
  start_line: number;
  end_line: number;
  content: string;
};

type AskResponse = {
  question: string;
  repository_id: number;
  answer: string;
  contexts: AskContext[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepoId, setSelectedRepoId] = useState<number | "">("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskResponse | null>(null);

  const [repoName, setRepoName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");

  const [isLoadingRepos, setIsLoadingRepos] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  const [error, setError] = useState("");
  const [importMessage, setImportMessage] = useState("");

  const selectedRepo = useMemo(
    () => repositories.find((repo) => repo.id === selectedRepoId),
    [repositories, selectedRepoId]
  );

  const fetchRepositories = async () => {
    try {
      setIsLoadingRepos(true);
      const res = await axios.get<Repository[]>(`${API_BASE_URL}/repositories/`);
      setRepositories(res.data);

      if (res.data.length > 0) {
        setSelectedRepoId((prev) => prev || res.data[0].id);
      } else {
        setSelectedRepoId("");
      }
    } catch (err) {
      console.error(err);
      setError("Failed to load repositories. Make sure the backend is running.");
    } finally {
      setIsLoadingRepos(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
  }, []);

 const handleImportRepository = async () => {
  if (!repoName.trim()) {
    setError("Please enter a repository name.");
    return;
  }

  if (!repoUrl.trim()) {
    setError("Please enter a GitHub repository URL.");
    return;
  }

  try {
    setIsImporting(true);
    setError("");
    setImportMessage("");

    const res = await axios.post<Repository>(`${API_BASE_URL}/repositories/`, {
      name: repoName.trim(),
      github_url: repoUrl.trim(),
    });

    const importedRepo = res.data;

    setImportMessage(`Repository "${importedRepo.name}" imported. Ingesting code chunks...`);

    await axios.post(`${API_BASE_URL}/repositories/${importedRepo.id}/ingest-chunks`);

    await fetchRepositories();
    setSelectedRepoId(importedRepo.id);

    setImportMessage(
      `Repository "${importedRepo.name}" imported and chunked successfully.`
    );
    setRepoName("");
    setRepoUrl("");
  } catch (err) {
    console.error(err);
    setError("Failed to import repository or ingest chunks.");
  } finally {
    setIsImporting(false);
  }
};

  const handleAsk = async () => {
    if (!selectedRepoId) {
      setError("Please select a repository.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      setIsAsking(true);
      setError("");
      setResponse(null);

    const res = await axios.post<AskResponse>(
  `${API_BASE_URL}/repositories/${selectedRepoId}/ask`,
  {
    question,
    limit: 5,
    code_only: true,
    exclude_docs: true,
    exclude_examples: true,
  }
);

      setResponse(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to get an answer from the backend.");
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-8">
          <p className="mb-2 text-sm uppercase tracking-[0.2em] text-cyan-400">
            RepoPilot
          </p>
          <h1 className="text-4xl font-bold tracking-tight">
            AI Software Engineering Assistant
          </h1>
          <p className="mt-3 max-w-3xl text-slate-300">
            Import repositories, ask repository-aware engineering questions, and
            inspect the retrieved code context behind each answer.
          </p>
        </header>

        <section className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <aside className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
              <h2 className="text-xl font-semibold">Import repository</h2>
              <p className="mt-2 text-sm text-slate-400">
                Add a public GitHub repository to RepoPilot.
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
                    Repository name
                  </label>
                  <input
                    type="text"
                    value={repoName}
                    onChange={(e) => setRepoName(e.target.value)}
                    placeholder="Example: fastapi-sample"
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none transition focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
                    GitHub URL
                  </label>
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/tiangolo/fastapi.git"
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none transition focus:border-cyan-500"
                  />
                </div>

                <button
                  onClick={handleImportRepository}
                  disabled={isImporting}
                  className="w-full rounded-xl bg-slate-100 px-4 py-3 font-medium text-slate-950 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isImporting ? "Importing..." : "Import Repository"}
                </button>

                {importMessage && (
                  <div className="rounded-xl border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-300">
                    {importMessage}
                  </div>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
              <h2 className="text-xl font-semibold">Ask the repository</h2>
              <p className="mt-2 text-sm text-slate-400">
                Choose a repository, write a technical question, and inspect the
                retrieved code chunks.
              </p>

              <div className="mt-6 space-y-5">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
                    Repository
                  </label>
                  <select
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none transition focus:border-cyan-500"
                    value={selectedRepoId}
                    onChange={(e) =>
                      setSelectedRepoId(
                        e.target.value ? Number(e.target.value) : ""
                      )
                    }
                    disabled={isLoadingRepos || repositories.length === 0}
                  >
                    {repositories.length === 0 ? (
                      <option value="">No repositories found</option>
                    ) : (
                      repositories.map((repo) => (
                        <option key={repo.id} value={repo.id}>
                          {repo.name} (ID: {repo.id})
                        </option>
                      ))
                    )}
                  </select>
                </div>

                {selectedRepo && (
                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-sm font-medium text-slate-200">
                      Selected repository
                    </p>
                    <p className="mt-2 text-sm text-slate-300">
                      {selectedRepo.name}
                    </p>
                    <p className="mt-1 break-all text-xs text-slate-500">
                      {selectedRepo.github_url}
                    </p>
                  </div>
                )}

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
                    Question
                  </label>
                  <textarea
                    className="min-h-[140px] w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none transition focus:border-cyan-500"
                    placeholder="Example: How does FastAPI include routers?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                  />
                </div>

                <button
                  onClick={handleAsk}
                  disabled={isAsking || isLoadingRepos}
                  className="w-full rounded-xl bg-cyan-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isAsking ? "Asking..." : "Ask RepoPilot"}
                </button>

                {error && (
                  <div className="rounded-xl border border-red-900 bg-red-950/40 p-3 text-sm text-red-300">
                    {error}
                  </div>
                )}
              </div>
            </div>
          </aside>

          <section className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
              <h2 className="text-xl font-semibold">Answer</h2>

              {!response ? (
                <div className="mt-4 rounded-xl border border-dashed border-slate-700 bg-slate-950 p-6 text-sm text-slate-400">
                  Ask a question to see the grounded repository response here.
                </div>
              ) : (
                <div className="mt-4 space-y-4">
                  <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wider text-slate-500">
                      Question
                    </p>
                    <p className="mt-2 text-sm text-slate-200">
                      {response.question}
                    </p>
                  </div>

                  <div className="rounded-xl border border-cyan-900 bg-cyan-950/30 p-4">
                    <p className="text-xs uppercase tracking-wider text-cyan-400">
                      Current answer
                    </p>
                    <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-100">
                      {response.answer}
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold">Retrieved Context</h2>
                <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                  {response?.contexts.length ?? 0} chunks
                </span>
              </div>

              {!response || response.contexts.length === 0 ? (
                <div className="mt-4 rounded-xl border border-dashed border-slate-700 bg-slate-950 p-6 text-sm text-slate-400">
                  No retrieved code context yet.
                </div>
              ) : (
                <div className="mt-4 space-y-4">
                  {response.contexts.map((context, index) => (
                    <article
                      key={`${context.file_path}-${context.chunk_index}-${index}`}
                      className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950"
                    >
                      <div className="border-b border-slate-800 px-4 py-3">
                        <p className="break-all font-mono text-sm text-cyan-300">
                          {context.file_path}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {context.file_type || "unknown"} • chunk{" "}
                          {context.chunk_index} • lines {context.start_line}-
                          {context.end_line}
                        </p>
                      </div>

                      <pre className="overflow-x-auto px-4 py-4 text-xs leading-6 text-slate-200">
                        <code>{context.content}</code>
                      </pre>
                    </article>
                  ))}
                </div>
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}