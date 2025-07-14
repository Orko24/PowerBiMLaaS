import React, { useState, useEffect } from 'react';
import { FlexCol, FlexRow } from '../../components/Flex';
import Btn from '../../components/Btn';
import PopupMenu from '../../components/PopupMenu';
import { mdiClose, mdiBrain, mdiChartLine, mdiDownload } from '@mdi/js';
import type { PrglState } from '../../App';
import { PromptToDAX } from './PromptToDAX';
import { PowerBIExport } from './PowerBIExport';

interface DashboardBuilderProps {
  table: string;
  dbs: PrglState['dbs'];
  dbsMethods: PrglState['dbsMethods'];
  onClose: () => void;
}

export const DashboardBuilder = ({ table, dbs, dbsMethods, onClose }: DashboardBuilderProps) => {
  const [columns, setColumns] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatedDAX, setGeneratedDAX] = useState<string>('');
  const [generatedSQL, setGeneratedSQL] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTableSchema();
  }, [table]);

  const fetchTableSchema = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await dbs.raw(`
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
      `, [table]);
      
      setColumns(result);
    } catch (error) {
      console.error('Error fetching table schema:', error);
      setError('Failed to fetch table schema');
    } finally {
      setLoading(false);
    }
  };

  const getApiBaseUrl = () => {
    // Vite uses import.meta.env, CRA uses process.env
    if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_AI_API_URL) {
      return import.meta.env.VITE_AI_API_URL;
    }
    if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_AI_API_URL) {
      return process.env.REACT_APP_AI_API_URL;
    }
    return 'http://localhost:8000';
  };
  const API_BASE_URL = getApiBaseUrl();

  const handleGenerateDashboard = async (prompt: string) => {
    setLoading(true);
    setError(null);
    try {
      // Call the backend API to generate DAX/SQL
      const response = await fetch(`${API_BASE_URL}/api/generate-dashboard`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table,
          prompt,
          columns: columns.map(col => ({ name: col.column_name, type: col.data_type }))
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate dashboard');
      }

      const data = await response.json();
      setGeneratedDAX(data.dax || '');
      setGeneratedSQL(data.sql || '');
    } catch (error) {
      console.error('Error generating dashboard:', error);
      setError('Failed to generate dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <PopupMenu
      title="AI Dashboard Builder"
      positioning="center"
      clickCatchStyle={{ opacity: 0.5 }}
      onClickClose={onClose}
      content={
        <FlexCol className="dashboard-builder p-4 gap-4" style={{ minWidth: '600px', maxWidth: '800px' }}>
          <FlexRow className="ai-center jc-between">
            <FlexRow className="ai-center gap-2">
              <i className="icon" style={{ backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(`<svg viewBox="0 0 24 24"><path fill="currentColor" d="${mdiBrain}"/></svg>")}")` }}></i>
              <h3 className="text-lg font-semibold">Create Dashboard for: {table}</h3>
            </FlexRow>
            <Btn
              onClick={onClose}
              iconPath={mdiClose}
              variant="text"
              color="danger"
            />
          </FlexRow>

          {error && (
            <div className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Left Panel - Prompt Input */}
            <FlexCol className="gap-3">
              <div>
                <h4 className="font-medium mb-2">Natural Language Prompt</h4>
                <PromptToDAX 
                  onGenerate={handleGenerateDashboard}
                  loading={loading}
                  table={table}
                  columns={columns}
                />
              </div>

              {columns.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Table Schema</h4>
                  <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-md max-h-40 overflow-y-auto">
                    <div className="text-sm">
                      {columns.map((col, index) => (
                        <div key={index} className="flex justify-between py-1">
                          <span className="font-mono">{col.column_name}</span>
                          <span className="text-gray-600 dark:text-gray-400">{col.data_type}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </FlexCol>

            {/* Right Panel - Generated Code */}
            <FlexCol className="gap-3">
              <div>
                <h4 className="font-medium mb-2">Generated DAX</h4>
                <div className="bg-gray-900 text-green-400 p-3 rounded-md font-mono text-sm max-h-40 overflow-y-auto">
                  {generatedDAX ? (
                    <pre className="whitespace-pre-wrap">{generatedDAX}</pre>
                  ) : (
                    <span className="text-gray-500">Enter a prompt to generate DAX code...</span>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Generated SQL</h4>
                <div className="bg-gray-900 text-blue-400 p-3 rounded-md font-mono text-sm max-h-40 overflow-y-auto">
                  {generatedSQL ? (
                    <pre className="whitespace-pre-wrap">{generatedSQL}</pre>
                  ) : (
                    <span className="text-gray-500">Enter a prompt to generate SQL code...</span>
                  )}
                </div>
              </div>

              {generatedDAX && (
                <PowerBIExport 
                  table={table}
                  daxCode={generatedDAX}
                  sqlCode={generatedSQL}
                  columns={columns}
                />
              )}
            </FlexCol>
          </div>
        </FlexCol>
      }
    />
  );
}; 