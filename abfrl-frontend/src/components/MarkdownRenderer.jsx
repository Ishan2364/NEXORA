// src/components/MarkdownRenderer.jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MarkdownRenderer.css'; // We will create this next

const MarkdownRenderer = ({ content }) => {
  return (
    <div className="markdown-content">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]} // This enables Table support
        components={{
          // Optional: Custom styling for specific elements
          table: ({node, ...props}) => <table className="styled-table" {...props} />,
          p: ({node, ...props}) => <p style={{ marginBottom: '10px' }} {...props} />
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;