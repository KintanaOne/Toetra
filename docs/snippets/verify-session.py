from toetra import verify

session = verify("policy.toetra", model="model.joblib", dataset="reference.csv")
session.print()
session.write_artifacts("artifacts", formats={"json", "html"})
raise SystemExit(session.exit_code)
