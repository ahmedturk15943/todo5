# Vercel Deployment Guide

## Deployed URLs
- **Frontend**: https://frontend-mauve-iota-87.vercel.app
- **Backend**: https://backend-gamma-seven-21.vercel.app
- **GitHub Repo**: https://github.com/ahmedturk15943/todo2.git

## Environment Variables Configuration

### Backend Variables (Required)
Set these at: https://vercel.com/ahmed-raza-turks-projects/backend/settings/environment-variables

```
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=<generate-with-python-secrets>
CORS_ORIGINS=https://frontend-mauve-iota-87.vercel.app
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
DEBUG=false
LOG_LEVEL=INFO
```

### Frontend Variables (Required)
Set these at: https://vercel.com/ahmed-raza-turks-projects/frontend/settings/environment-variables

```
NEXT_PUBLIC_API_URL=https://backend-gamma-seven-21.vercel.app
BETTER_AUTH_SECRET=<same-as-backend>
BETTER_AUTH_URL=https://frontend-mauve-iota-87.vercel.app
```

## Generate Secure Secret

Run this command to generate a secure secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the same secret for both `BETTER_AUTH_SECRET` variables.

## Database Setup

1. Create a Neon PostgreSQL database at https://neon.tech
2. Run the initialization script from `backend/scripts/init_db.sql`
3. Copy the connection string and add it to `DATABASE_URL`

## After Setting Environment Variables

1. Redeploy backend:
   ```bash
   cd backend
   vercel --prod
   ```

2. Redeploy frontend:
   ```bash
   cd frontend
   vercel --prod
   ```

## Testing the Deployment

1. Visit the frontend URL: https://frontend-mauve-iota-87.vercel.app
2. Click "Sign Up" to create an account
3. Sign in and start managing tasks

## Troubleshooting

### Backend Issues
- Check logs: `vercel logs https://backend-gamma-seven-21.vercel.app`
- Verify DATABASE_URL is correct and database is accessible
- Ensure CORS_ORIGINS includes the frontend URL

### Frontend Issues
- Check logs: `vercel logs https://frontend-mauve-iota-87.vercel.app`
- Verify NEXT_PUBLIC_API_URL points to backend
- Check browser console for API connection errors

## Custom Domain (Optional)

To add a custom domain:
1. Go to project settings in Vercel dashboard
2. Add your domain
3. Update DNS records as instructed
4. Update environment variables with new domain URLs
