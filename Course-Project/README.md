# Course project

The main application is contained here: [backend](./backend/) provides the Express API, agents and workflow; [frontend](./frontend/) provides the React/Vite console. The independent [Python edition](./langgraph_edition/) retains separate startup/storage. All fourteen notebooks and scripts remain in repository-root [Assignments](../Assignments/README.md).

## Run from this folder

```sh
npm --prefix backend ci
npm --prefix frontend ci
npm --prefix frontend run build
```

Copy backend/.env.example to backend/.env only for a new installation; preserve existing local settings. Then run `npm start` from backend and open http://localhost:3000. Windows launchers: [setup.bat](setup.bat), [start.bat](start.bat), [verify.bat](verify.bat).

## Technical documentation

- [Original problem statement](Problem_Statement/Research_Grant_Management_System.docx)
- [Scope mapping](docs/SCOPE_MAPPING.md)
- [Technical documentation](docs/README.md)
- [Final report: Markdown/DOCX/PDF](Final_Report/README.md)
- [Fresh verification](docs/VERIFICATION.md)
- [Historical evidence](evidence/README.md)

The root README contains the team's corrected names/USNs and B-DIV for all four members. Blank course originals and immutable saved history remain unchanged.
