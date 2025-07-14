import React, { useState, useEffect } from 'react';
import { FlexCol, FlexRow } from '../../components/Flex';
import Btn from '../../components/Btn';
import { mdiChartLine, mdiDatabase, mdiPlus, mdiBrain } from '@mdi/js';
import type { PrglState } from '../../App';
import { DashboardBuilder } from './DashboardBuilder';

export const AIAnalyticsDashboard = ({ dbs, dbsMethods, ...props }: PrglState) => {
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [showBuilder, setShowBuilder] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use the existing dbs connection to get tables
      const result = await dbs.raw(`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
      `);
      
      const tableList = result.map((row: any) => row.table_name);
      setTables(tableList);
    } catch (error) {
      console.error('Error fetching tables:', error);
      setError('Failed to fetch tables from database');
    } finally {
      setLoading(false);
    }
  };

  return (
    <FlexCol className="ai-analytics-dashboard p-4 gap-4">
      <FlexRow className="ai-center jc-between">
        <FlexRow className="ai-center gap-2">
          <i className="icon" style={{ backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(`<svg viewBox="0 0 24 24"><path fill="currentColor" d="${mdiBrain}"/></svg>")}")` }}></i>
          <h2 className="text-xl font-bold">AI Analytics Dashboard</h2>
        </FlexRow>
      </FlexRow>

      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Create AI-Powered Dashboard</h3>
        
        <FlexRow className="controls gap-3 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">Select Database Table</label>
            <select 
              value={selectedTable} 
              onChange={(e) => setSelectedTable(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
              disabled={loading}
            >
              <option value="">Choose a table...</option>
              {tables.map(table => (
                <option key={table} value={table}>{table}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <Btn 
              onClick={() => setShowBuilder(true)}
              disabled={!selectedTable || loading}
              iconPath={mdiPlus}
              variant="filled"
              color="action"
            >
              Create Dashboard
            </Btn>
          </div>
        </FlexRow>

        {error && (
          <div className="text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-md mb-4">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-gray-600 dark:text-gray-400">
            Loading tables...
          </div>
        )}

        {tables.length > 0 && !loading && (
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Found {tables.length} table{tables.length !== 1 ? 's' : ''} in your database
          </div>
        )}
      </div>

      {showBuilder && selectedTable && (
        <DashboardBuilder 
          table={selectedTable}
          dbs={dbs}
          dbsMethods={dbsMethods}
          onClose={() => setShowBuilder(false)}
        />
      )}
    </FlexCol>
  );
}; 