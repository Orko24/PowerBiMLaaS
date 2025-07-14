import React from 'react';
import { FlexCol, FlexRow } from '../../components/Flex';
import Btn from '../../components/Btn';
import { mdiDownload, mdiMicrosoftPowerbi, mdiDatabase } from '@mdi/js';

interface PowerBIExportProps {
  table: string;
  daxCode: string;
  sqlCode: string;
  columns: any[];
}

export const PowerBIExport = ({ table, daxCode, sqlCode, columns }: PowerBIExportProps) => {
  const getApiBaseUrl = () => {
    if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_AI_API_URL) {
      return import.meta.env.VITE_AI_API_URL;
    }
    if (typeof process !== 'undefined' && process.env && process.env.REACT_APP_AI_API_URL) {
      return process.env.REACT_APP_AI_API_URL;
    }
    return 'http://localhost:8000';
  };
  const API_BASE_URL = getApiBaseUrl();
  const generatePBIDS = () => {
    const pbidsContent = {
      version: "1.0",
      connections: [{
        filePath: `${API_BASE_URL}/api/dashboard/${table}/data`,
        name: table
      }]
    };
    
    const blob = new Blob([JSON.stringify(pbidsContent, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${table}_dashboard.pbids`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadDAX = () => {
    const blob = new Blob([daxCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${table}_dashboard.dax`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadSQL = () => {
    const blob = new Blob([sqlCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${table}_query.sql`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <FlexCol className="powerbi-export gap-3">
      <h4 className="font-medium mb-2">Export Options</h4>
      
      <FlexRow className="gap-2 flex-wrap">
        <Btn
          onClick={generatePBIDS}
          iconPath={mdiMicrosoftPowerbi}
          variant="filled"
          color="action"
          size="small"
        >
          Download .pbids
        </Btn>
        
        <Btn
          onClick={downloadDAX}
          iconPath={mdiDownload}
          variant="outlined"
          color="action"
          size="small"
        >
          Download DAX
        </Btn>
        
        <Btn
          onClick={downloadSQL}
          iconPath={mdiDatabase}
          variant="outlined"
          color="action"
          size="small"
        >
          Download SQL
        </Btn>
      </FlexRow>

      <div className="text-xs text-gray-600 dark:text-gray-400">
        <strong>Instructions:</strong>
        <ul className="list-disc list-inside mt-1 space-y-1">
          <li>Download .pbids file and open in Power BI Desktop</li>
          <li>Use the DAX code in Power BI measures</li>
          <li>Use the SQL code for direct database queries</li>
        </ul>
      </div>
    </FlexCol>
  );
}; 