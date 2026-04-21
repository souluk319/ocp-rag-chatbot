import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import WorkspacePage from '../pages/WorkspacePage';
import LlmWikiBookPage from '../pages/LlmWikiBookPage';
import PlaybookLibraryPage from '../pages/PlaybookLibraryPage';
import ProjectDetailsPage from '../pages/ProjectDetailsPage';
import PartnerNamespacePage from '../partner/PartnerNamespacePage';
import SharedLandingShell from '../shared/landing/SharedLandingShell';
import { buildHandoffLocation } from './handoff';
import { ROUTES } from './routes';

function AliasRedirect({ to }: { to: string }) {
  const location = useLocation();

  return (
    <Navigate
      replace
      to={buildHandoffLocation(to, location)}
    />
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.sharedHome} element={<SharedLandingShell />} />
      <Route path={ROUTES.pbsDetails} element={<ProjectDetailsPage />} />
      <Route path={ROUTES.pbsStudio} element={<WorkspacePage />} />
      <Route path={ROUTES.pbsWikiBook} element={<LlmWikiBookPage />} />
      <Route path={ROUTES.pbsWikiBookAlias} element={<AliasRedirect to={ROUTES.pbsWikiBook} />} />
      <Route path={ROUTES.pbsWorkspaceAlias} element={<AliasRedirect to={ROUTES.pbsStudio} />} />
      <Route path={ROUTES.pbsPlaybookLibrary} element={<PlaybookLibraryPage />} />
      <Route path={ROUTES.pbsControlTower} element={<PlaybookLibraryPage />} />
      <Route path={ROUTES.pbsRepository} element={<PlaybookLibraryPage />} />
      <Route
        path={ROUTES.partnerHome}
        element={(
          <PartnerNamespacePage
            eyebrow="Partner Lane"
            title="Reserved partner namespace"
            description="다른 프로젝트 기능은 PBS route family를 침범하지 않고 sibling namespace 아래에서 병합됩니다."
          />
        )}
      />
      <Route
        path={ROUTES.partnerWorkspace}
        element={(
          <PartnerNamespacePage
            eyebrow="Partner Workspace"
            title="Partner workspace handoff"
            description="상대 프로젝트의 작업 공간은 이 sibling namespace로 유입되고, PBS workspace state와 분리됩니다."
          />
        )}
      />
      <Route
        path={ROUTES.partnerLibrary}
        element={(
          <PartnerNamespacePage
            eyebrow="Partner Library"
            title="Partner library reservation"
            description="상대 프로젝트 library 진입면은 이 경로에 들어오고, PBS Playbook Library와 canonical truth를 공유하지 않습니다."
          />
        )}
      />
      <Route
        path={ROUTES.partnerViewer}
        element={(
          <PartnerNamespacePage
            eyebrow="Partner Viewer"
            title="Partner viewer reservation"
            description="상대 프로젝트 viewer는 reserved namespace로 분리되며, PBS wiki runtime viewer deep link와 충돌하지 않습니다."
          />
        )}
      />
      <Route
        path={ROUTES.partnerDetails}
        element={(
          <PartnerNamespacePage
            eyebrow="Partner Details"
            title="Partner details placeholder"
            description="공유 랜딩은 여기로 handoff할 수 있지만, 제품 소개와 runtime truth ownership은 PBS 바깥 sibling lane에 남습니다."
          />
        )}
      />
      <Route path="*" element={<Navigate replace to={ROUTES.sharedHome} />} />
    </Routes>
  );
}
