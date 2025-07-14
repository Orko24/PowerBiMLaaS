import React, { useState } from 'react';
import { FlexCol, FlexRow } from '../../components/Flex';
import Btn from '../../components/Btn';
import { mdiBrain, mdiSend } from '@mdi/js';

interface PromptToDAXProps {
  onGenerate: (prompt: string) => void;
  loading: boolean;
  table: string;
  columns: any[];
}

export const PromptToDAX = ({ onGenerate, loading, table, columns }: PromptToDAXProps) => {
  const [prompt, setPrompt] = useState<string>('');
  const [showExamples, setShowExamples] = useState<boolean>(false);

  const examplePrompts = [
    `Show me total fraud by month`,
    `Create a chart showing fraud amount trends over time`,
    `Display fraud percentage by category`,
    `Show top 10 fraudulent transactions`,
    `Create a dashboard with fraud detection metrics`,
    `Show fraud patterns by location`,
    `Display fraud vs legitimate transaction ratios`,
    `Create a time series of fraud incidents`
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !loading) {
      onGenerate(prompt.trim());
    }
  };

  const useExamplePrompt = (example: string) => {
    setPrompt(example);
    setShowExamples(false);
  };

  return (
    <FlexCol className="prompt-to-dax gap-3">
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want to analyze... (e.g., 'Show me total fraud by month')"
            className="w-full p-3 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 resize-none"
            rows={4}
            disabled={loading}
          />
        </div>
        
        <FlexRow className="ai-center jc-between">
          <Btn
            type="button"
            onClick={() => setShowExamples(!showExamples)}
            variant="text"
            color="action"
            disabled={loading}
          >
            {showExamples ? 'Hide' : 'Show'} Examples
          </Btn>
          
          <Btn
            type="submit"
            onClick={handleSubmit}
            disabled={!prompt.trim() || loading}
            iconPath={mdiSend}
            variant="filled"
            color="action"
          >
            {loading ? 'Generating...' : 'Generate Dashboard'}
          </Btn>
        </FlexRow>
      </form>

      {showExamples && (
        <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-md">
          <h5 className="font-medium mb-2 text-sm">Example Prompts:</h5>
          <div className="grid grid-cols-1 gap-2">
            {examplePrompts.map((example, index) => (
              <button
                key={index}
                onClick={() => useExamplePrompt(example)}
                className="text-left p-2 text-sm bg-white dark:bg-gray-600 rounded border hover:bg-gray-50 dark:hover:bg-gray-500 transition-colors"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}

      {columns.length > 0 && (
        <div className="text-xs text-gray-600 dark:text-gray-400">
          <strong>Available columns:</strong> {columns.map(col => col.column_name).join(', ')}
        </div>
      )}
    </FlexCol>
  );
}; 