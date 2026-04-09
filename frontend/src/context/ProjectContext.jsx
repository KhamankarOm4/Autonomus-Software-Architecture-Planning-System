import React, { createContext, useContext, useState } from 'react';

const ProjectContext = createContext(null);

export const useProjectContext = () => useContext(ProjectContext);

export const ProjectProvider = ({ children }) => {
  const [projectData, setProjectData] = useState({
    name: '',
    mode: 'greenfield', // 'greenfield' or 'brownfield'
    requirements: '', // for greenfield
    input: '', // for brownfield (path or snippet)
  });

  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateProjectData = (data) => {
    setProjectData((prev) => ({ ...prev, ...data }));
  };

  const resetProject = () => {
    setProjectData({ name: '', mode: 'greenfield', requirements: '', input: '' });
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <ProjectContext.Provider
      value={{
        projectData,
        updateProjectData,
        analysisResult,
        setAnalysisResult,
        isLoading,
        setIsLoading,
        error,
        setError,
        resetProject,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};
