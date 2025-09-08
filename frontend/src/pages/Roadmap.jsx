import React, { useState } from 'react';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { CheckCircle, Clock, Calendar, Target } from 'lucide-react';
import { roadmapPhases, milestones } from '../data/roadmapData';

const StatusIcon = ({ status }) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-6 h-6 text-green-400" />;
    case 'in-progress':
      return <Clock className="w-6 h-6 text-accent-cyan" />;
    case 'planned':
      return <Calendar className="w-6 h-6 text-royal-blue" />;
    case 'future':
      return <Target className="w-6 h-6 text-text-muted" />;
    default:
      return <Calendar className="w-6 h-6 text-text-muted" />;
  }
};

const ProgressBar = ({ completion, color }) => (
  <div className="w-full bg-bg-secondary rounded-full h-2 mb-4">
    <div 
      className={`h-2 rounded-full transition-all duration-1000 ease-out ${
        completion > 0 ? 'bg-green-400' : 'bg-text-muted'
      }`}
      style={{ width: `${completion}%` }}
    />
  </div>
);

export default function Roadmap() {
  const [selectedPhase, setSelectedPhase] = useState(null);

  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      
      <main className="pt-24">
        {/* Hero Section */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="display-large mb-6">خارطة الطريق</h1>
              <p className="body-large text-text-secondary mb-8 max-w-2xl mx-auto">
                رحلة Regam Blockchain من الإطلاق إلى منصة بلوك تشين شاملة. 
                تابع تقدمنا عبر 8 مراحل تطوير استراتيجية.
              </p>
            </div>
          </div>
        </section>

        {/* Milestones Overview */}
        <section className="py-12">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <h2 className="display-medium text-center mb-12">المعالم الرئيسية</h2>
              <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4">
                {milestones.map((milestone, index) => (
                  <Card key={index} className="stat-card text-center">
                    <CardContent className="p-4">
                      <p className="body-small text-text-muted mb-2">{milestone.date}</p>
                      <p className="body-small font-semibold mb-2">{milestone.title}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Interactive Roadmap Timeline */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-6xl mx-auto">
              <div className="relative">
                {/* Timeline Line */}
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border-subtle"></div>
                
                {/* Timeline Items */}
                <div className="space-y-12">
                  {roadmapPhases.map((phase, index) => (
                    <div 
                      key={phase.id}
                      className={`relative flex items-start cursor-pointer transition-all duration-300 ${
                        selectedPhase === phase.id ? 'transform scale-105' : ''
                      }`}
                      onClick={() => setSelectedPhase(selectedPhase === phase.id ? null : phase.id)}
                    >
                      {/* Timeline Dot */}
                      <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full ${phase.bgColor} ${phase.borderColor} border-2 mr-8`}>
                        <div className="flex flex-col items-center">
                          <StatusIcon status={phase.status} />
                          <span className="text-xs font-bold mt-1">{phase.id}</span>
                        </div>
                      </div>

                      {/* Content Card */}
                      <div className="flex-1">
                        <Card className={`value-card transition-all duration-300 ${
                          selectedPhase === phase.id ? 'ring-2 ring-accent-cyan' : ''
                        }`}>
                          <CardContent className="p-8">
                            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
                              <div className="flex-1">
                                <div className="flex items-center gap-4 mb-3">
                                  <h3 className="heading-2">{phase.title}</h3>
                                  <Badge 
                                    variant="secondary" 
                                    className={`${phase.color} border-current`}
                                  >
                                    {phase.quarter}
                                  </Badge>
                                </div>
                                <p className="body-medium text-text-secondary mb-4">
                                  {phase.description}
                                </p>
                                
                                {/* Progress Bar */}
                                <div className="mb-4">
                                  <div className="flex justify-between items-center mb-2">
                                    <span className="body-small text-text-muted">التقدم</span>
                                    <span className={`body-small font-bold ${phase.color}`}>
                                      {phase.completion}%
                                    </span>
                                  </div>
                                  <ProgressBar completion={phase.completion} color={phase.color} />
                                </div>

                                {/* Status Badge */}
                                <Badge 
                                  variant="outline" 
                                  className={`${phase.color} border-current`}
                                >
                                  {phase.status === 'completed' && '✅ مكتمل'}
                                  {phase.status === 'in-progress' && '🚧 جاري العمل'}
                                  {phase.status === 'planned' && '📅 مخطط'}
                                  {phase.status === 'future' && '🔮 مستقبلي'}
                                </Badge>
                              </div>
                            </div>

                            {/* Achievements List - Expandable */}
                            {selectedPhase === phase.id && (
                              <div className="mt-6 pt-6 border-t border-border-subtle animate-in slide-in-from-top duration-300">
                                <h4 className="heading-3 mb-4">الإنجازات المتوقعة:</h4>
                                <div className="grid md:grid-cols-2 gap-3">
                                  {phase.achievements.map((achievement, achieveIndex) => (
                                    <div 
                                      key={achieveIndex}
                                      className="flex items-start gap-3 p-3 rounded-lg bg-bg-primary"
                                    >
                                      {phase.status === 'completed' ? (
                                        <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                                      ) : (
                                        <div className="w-5 h-5 rounded-full border-2 border-current mt-0.5 flex-shrink-0 opacity-50" />
                                      )}
                                      <span className="body-small text-text-secondary">
                                        {achievement}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Click Hint */}
                            {selectedPhase !== phase.id && (
                              <div className="mt-4 text-center">
                                <span className="body-small text-text-muted">
                                  انقر لعرض التفاصيل...
                                </span>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Summary */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto">
              <h2 className="display-medium text-center mb-12">إحصائيات التقدم</h2>
              <div className="grid md:grid-cols-4 gap-6">
                <Card className="stat-card text-center">
                  <CardContent className="p-6">
                    <p className="heading-1 text-green-400 mb-2">
                      {roadmapPhases.filter(p => p.status === 'completed').length}
                    </p>
                    <p className="body-small text-text-muted">مراحل مكتملة</p>
                  </CardContent>
                </Card>
                <Card className="stat-card text-center">
                  <CardContent className="p-6">
                    <p className="heading-1 text-accent-cyan mb-2">
                      {roadmapPhases.filter(p => p.status === 'in-progress').length}
                    </p>
                    <p className="body-small text-text-muted">قيد التطوير</p>
                  </CardContent>
                </Card>
                <Card className="stat-card text-center">
                  <CardContent className="p-6">
                    <p className="heading-1 text-royal-blue mb-2">
                      {roadmapPhases.filter(p => p.status === 'planned').length}
                    </p>
                    <p className="body-small text-text-muted">مخططة</p>
                  </CardContent>
                </Card>
                <Card className="stat-card text-center">
                  <CardContent className="p-6">
                    <p className="heading-1 text-gold-accent mb-2">
                      {Math.round(roadmapPhases.reduce((acc, p) => acc + p.completion, 0) / roadmapPhases.length)}%
                    </p>
                    <p className="body-small text-text-muted">التقدم الإجمالي</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16">
          <div className="dark-container">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="display-medium mb-6">كن جزءًا من الرحلة</h2>
              <p className="body-large text-text-secondary mb-8 max-w-2xl mx-auto">
                انضم إلى مجتمع Regam Blockchain وتابع تقدمنا في بناء مستقبل التمويل اللامركزي.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="btn-primary">
                  انضم للمجتمع
                </button>
                <button className="btn-secondary">
                  تابع التحديثات
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}