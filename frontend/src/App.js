import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [stage, setStage] = useState('start'); // start, test, results
  const [sex, setSex] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentBlock, setCurrentBlock] = useState(1);
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Fetch questions on mount
  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/questions`);
      const data = await response.json();
      setQuestions(data.questions);
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const startTest = async () => {
    if (!sex) {
      alert('Por favor, selecciona tu sexo para comenzar');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/start-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sex })
      });
      const data = await response.json();
      setSessionId(data.session_id);
      setStage('test');
    } catch (error) {
      console.error('Error starting test:', error);
      alert('Error al iniciar el test');
    }
    setLoading(false);
  };

  const handleResponseChange = async (questionNumber, option) => {
    const currentResponse = responses[questionNumber] || [];
    let newResponse;

    if (currentResponse.includes(option)) {
      // Remove option
      newResponse = currentResponse.filter(o => o !== option);
    } else {
      // Add option
      newResponse = [...currentResponse, option];
    }

    setResponses({
      ...responses,
      [questionNumber]: newResponse
    });

    // Save to backend
    try {
      await fetch(`${BACKEND_URL}/api/save-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question_number: questionNumber,
          response: newResponse
        })
      });
    } catch (error) {
      console.error('Error saving response:', error);
    }
  };

  const completeTest = async () => {
    // Check if all questions are answered
    const unansweredCount = questions.length - Object.keys(responses).length;
    
    if (unansweredCount > 0) {
      const confirm = window.confirm(
        `Tienes ${unansweredCount} preguntas sin responder. ¿Deseas continuar de todas formas?`
      );
      if (!confirm) return;
    }

    setLoading(true);
    try {
      await fetch(`${BACKEND_URL}/api/complete-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      
      // Fetch results
      const resultsResponse = await fetch(`${BACKEND_URL}/api/results/${sessionId}`);
      const resultsData = await resultsResponse.json();
      setResults(resultsData);
      
      setStage('results');
    } catch (error) {
      console.error('Error completing test:', error);
      alert('Error al completar el test');
    }
    setLoading(false);
  };

  const getBlockQuestions = () => {
    return questions.filter(q => q.block === currentBlock);
  };

  const getProgress = () => {
    return Math.round((Object.keys(responses).length / questions.length) * 100);
  };

  const getBlockProgress = () => {
    const blockQuestions = getBlockQuestions();
    const answeredInBlock = blockQuestions.filter(q => responses[q.number]).length;
    return Math.round((answeredInBlock / blockQuestions.length) * 100);
  };

  // Start Screen
  if (stage === 'start') {
    return (
      <div className="app-container">
        <div className="start-screen">
          <div className="logo-container">
            <div className="logo-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
          </div>
          
          <h1 className="main-title">CASM-83 R2014</h1>
          <p className="subtitle">Inventario de Intereses Vocacionales y Ocupacionales</p>
          
          <div className="info-card">
            <h2>Instrucciones</h2>
            <ul>
              <li>Este test consta de 143 preguntas organizadas en 11 bloques</li>
              <li>Cada pregunta presenta dos opciones (A y B)</li>
              <li>Puedes marcar una, ambas o ninguna opción según tus preferencias</li>
              <li>No hay respuestas correctas o incorrectas</li>
              <li>Responde con sinceridad según tus verdaderos intereses</li>
            </ul>
          </div>

          <div className="sex-selection">
            <h3>Para comenzar, selecciona tu sexo:</h3>
            <div className="sex-buttons">
              <button 
                className={`sex-btn ${sex === 'masculino' ? 'active' : ''}`}
                onClick={() => setSex('masculino')}
              >
                <span className="icon">👨</span>
                Masculino
              </button>
              <button 
                className={`sex-btn ${sex === 'femenino' ? 'active' : ''}`}
                onClick={() => setSex('femenino')}
              >
                <span className="icon">👩</span>
                Femenino
              </button>
            </div>
          </div>

          <button 
            className="primary-btn"
            onClick={startTest}
            disabled={!sex || loading}
          >
            {loading ? 'Iniciando...' : 'Comenzar Test'}
          </button>
        </div>
      </div>
    );
  }

  // Test Screen
  if (stage === 'test') {
    const blockQuestions = getBlockQuestions();

    return (
      <div className="app-container">
        <div className="test-screen">
          {/* Header */}
          <div className="test-header">
            <div className="header-content">
              <h2>CASM-83 R2014</h2>
              <div className="progress-info">
                <span>Progreso Total: {getProgress()}%</span>
                <span className="separator">|</span>
                <span>Bloque {currentBlock} de 11</span>
              </div>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${getProgress()}%` }}></div>
            </div>
          </div>

          {/* Block Navigation */}
          <div className="block-navigation">
            <div className="block-tabs">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map(block => {
                const blockQs = questions.filter(q => q.block === block);
                const answered = blockQs.filter(q => responses[q.number]).length;
                const isComplete = answered === blockQs.length;
                
                return (
                  <button
                    key={block}
                    className={`block-tab ${
                      currentBlock === block ? 'active' : ''
                    } ${isComplete ? 'complete' : ''}`}
                    onClick={() => setCurrentBlock(block)}
                  >
                    <span className="block-number">{block}</span>
                    <span className="block-status">{answered}/{blockQs.length}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Block Progress */}
          <div className="block-progress">
            <div className="block-progress-header">
              <h3>Bloque {currentBlock}</h3>
              <span className="block-progress-text">{getBlockProgress()}% completado</span>
            </div>
            <div className="progress-bar small">
              <div className="progress-fill" style={{ width: `${getBlockProgress()}%` }}></div>
            </div>
          </div>

          {/* Questions */}
          <div className="questions-container">
            {blockQuestions.map((question) => {
              const currentResponse = responses[question.number] || [];
              const isAChecked = currentResponse.includes('A');
              const isBChecked = currentResponse.includes('B');

              return (
                <div key={question.number} className="question-card">
                  <div className="question-header">
                    <span className="question-number">Pregunta {question.number}</span>
                    {currentResponse.length > 0 && (
                      <span className="answered-badge">Respondida</span>
                    )}
                  </div>

                  <div className="question-options">
                    <label className={`option ${isAChecked ? 'checked' : ''}`}>
                      <input
                        type="checkbox"
                        checked={isAChecked}
                        onChange={() => handleResponseChange(question.number, 'A')}
                      />
                      <div className="option-content">
                        <div className="option-letter">A</div>
                        <div className="option-text">{question.optionA}</div>
                      </div>
                    </label>

                    <label className={`option ${isBChecked ? 'checked' : ''}`}>
                      <input
                        type="checkbox"
                        checked={isBChecked}
                        onChange={() => handleResponseChange(question.number, 'B')}
                      />
                      <div className="option-content">
                        <div className="option-letter">B</div>
                        <div className="option-text">{question.optionB}</div>
                      </div>
                    </label>
                  </div>

                  <div className="question-footer">
                    <span className="hint">
                      Puedes marcar una, ambas o ninguna opción
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Navigation Buttons */}
          <div className="test-navigation">
            <button
              className="nav-btn secondary"
              onClick={() => setCurrentBlock(Math.max(1, currentBlock - 1))}
              disabled={currentBlock === 1}
            >
              ← Bloque Anterior
            </button>

            {currentBlock < 11 ? (
              <button
                className="nav-btn primary"
                onClick={() => setCurrentBlock(Math.min(11, currentBlock + 1))}
              >
                Siguiente Bloque →
              </button>
            ) : (
              <button
                className="nav-btn complete"
                onClick={completeTest}
                disabled={loading}
              >
                {loading ? 'Finalizando...' : 'Finalizar Test ✓'}
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Results Screen
  if (stage === 'results') {
    if (!results) {
      return (
        <div className="app-container">
          <div className="results-screen">
            <div className="loading">Calculando resultados...</div>
          </div>
        </div>
      );
    }

    const interpretationLabels = {
      'desinteres': 'Desinterés',
      'bajo': 'Bajo',
      'promedio_bajo': 'Promedio Bajo',
      'indeciso': 'Indeciso',
      'promedio': 'Promedio',
      'promedio_alto': 'Promedio Alto',
      'alto': 'Alto',
      'muy_alto': 'Muy Alto'
    };

    const scoresArray = Object.entries(results.scores).map(([code, data]) => ({
      code,
      ...data
    }));

    return (
      <div className="app-container results-container">
        <div className="results-screen">
          {/* Header */}
          <div className="results-header">
            <div className="success-icon">✓</div>
            <h1>¡Test Completado!</h1>
            <p>Resultados del CASM-83 R2014</p>
          </div>

          {/* Gráfica de Resultados */}
          <div className="results-card">
            <h2>📊 Gráfica de Intereses por Escala</h2>
            <p className="chart-subtitle">Cantidad de respuestas por cada área vocacional</p>
            
            <div className="chart-container">
              {scoresArray.map((scale) => (
                <div key={scale.code} className="chart-bar-row">
                  <div className="chart-label">
                    <span className="scale-name">{scale.name}</span>
                    <span className="scale-score">{scale.score}/22</span>
                  </div>
                  <div className="chart-bar-container">
                    <div 
                      className="chart-bar"
                      style={{ 
                        width: `${(scale.score / 22) * 100}%`,
                        background: scale.interpretation === 'muy_alto' || scale.interpretation === 'alto' 
                          ? 'linear-gradient(90deg, #10b981, #059669)'
                          : scale.interpretation === 'promedio_alto' || scale.interpretation === 'promedio'
                          ? 'linear-gradient(90deg, #667eea, #764ba2)'
                          : 'linear-gradient(90deg, #94a3b8, #64748b)'
                      }}
                    >
                      <span className="chart-bar-label">
                        {interpretationLabels[scale.interpretation]}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recomendaciones de Carreras */}
          {results.recommendations.top_scales && results.recommendations.top_scales.length > 0 && (
            <div className="results-card">
              <h2>🎓 Recomendaciones Profesionales</h2>
              <p className="recommendations-subtitle">
                Basado en tus resultados, estas son las áreas donde mostraste mayor interés:
              </p>

              {results.recommendations.top_scales.map((rec, index) => (
                <div key={rec.scale} className="recommendation-card">
                  <div className="recommendation-header">
                    <span className="recommendation-number">#{index + 1}</span>
                    <div>
                      <h3>{rec.name}</h3>
                      <p className="recommendation-score">
                        Puntuación: {rec.score}/22 - {interpretationLabels[rec.interpretation]}
                      </p>
                    </div>
                  </div>

                  {rec.ocupaciones && rec.ocupaciones.length > 0 && (
                    <div className="career-section">
                      <h4>Carreras Profesionales:</h4>
                      <ul className="career-list">
                        {rec.ocupaciones.map((career, i) => (
                          <li key={i}>{career}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {rec.tecnicas && rec.tecnicas.length > 0 && (
                    <div className="career-section">
                      <h4>Carreras Técnicas:</h4>
                      <ul className="career-list">
                        {rec.tecnicas.map((career, i) => (
                          <li key={i}>{career}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Resumen */}
          <div className="results-card">
            <h2>📋 Resumen</h2>
            <div className="results-stats">
              <div className="stat">
                <div className="stat-value">{results.answered_questions}</div>
                <div className="stat-label">Preguntas Respondidas</div>
              </div>
              <div className="stat">
                <div className="stat-value">{results.recommendations.top_scales?.length || 0}</div>
                <div className="stat-label">Áreas Destacadas</div>
              </div>
              <div className="stat">
                <div className="stat-value">{sex === 'masculino' ? 'M' : 'F'}</div>
                <div className="stat-label">Sexo</div>
              </div>
            </div>

            <div className="session-info">
              <p><strong>ID de Sesión:</strong> {sessionId}</p>
            </div>
          </div>

          {/* Botón de nuevo test */}
          <button 
            className="primary-btn"
            onClick={() => {
              setStage('start');
              setSex('');
              setSessionId('');
              setResponses({});
              setCurrentBlock(1);
              setResults(null);
            }}
          >
            Realizar Nuevo Test
          </button>
        </div>
      </div>
    );
  }

  return null;
}

export default App;